/*
Copyright (c) 2018, Raspberry Pi (Trading) Ltd.
Copyright (c) 2013, Broadcom Europe Ltd.
Copyright (c) 2013, James Hughes
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the copyright holder nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

/**
 * \file RaspiStill.c
 * Command line program to capture a still frame and encode it to file.
 * Also optionally display a preview/viewfinder of current camera input.
 *
 * Description
 *
 * 3 components are created; camera, preview and JPG encoder.
 * Camera component has three ports, preview, video and stills.
 * This program connects preview and stills to the preview and jpg
 * encoder. Using mmal we don't need to worry about buffers between these
 * components, but we do need to handle buffers from the encoder, which
 * are simply written straight to the file in the requisite buffer callback.
 *
 * We use the RaspiCamControl code to handle the specific camera settings.
 */

// We use some GNU extensions (asprintf, basename)
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <memory.h>
#include <unistd.h>
#include <errno.h>
#include <sysexits.h>
#include <assert.h>
#include <stdarg.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <math.h>

#include "bcm_host.h"
#include "interface/vcos/vcos.h"

#include "interface/mmal/mmal.h"
#include "interface/mmal/mmal_logging.h"
#include "interface/mmal/mmal_buffer.h"
#include "interface/mmal/util/mmal_util.h"
#include "interface/mmal/util/mmal_util_params.h"
#include "interface/mmal/util/mmal_default_components.h"
#include "interface/mmal/util/mmal_connection.h"
#include "interface/mmal/mmal_parameters_camera.h"


#include "RaspiCamControl.h"
#include "RaspiPreview.h"
#include "RaspiHelpers.h"
#include "jsmn.h"
#include "DHT22.h"


#include <semaphore.h>
#include <math.h>
#include <pthread.h>
#include <time.h>
#include <wiringPi.h>

// Standard port setting for the camera component
#define MMAL_CAMERA_PREVIEW_PORT 0
#define MMAL_CAMERA_VIDEO_PORT 1
#define MMAL_CAMERA_CAPTURE_PORT 2

// Stills format information
// 0 implies variable
#define STILLS_FRAME_RATE_NUM 0
#define STILLS_FRAME_RATE_DEN 1

/// Video render needs at least 2 buffers.
#define VIDEO_OUTPUT_BUFFERS_NUM 3

#define MAX_EXIF_PAYLOAD_LENGTH 128
#define MAX_EXIF_LONG_PAYLOAD_LENGTH 256

#define CAMERA_NUM 0
#define SENSOR_MODE 0


/// Amount of time before first image taken to allow settling of
/// exposure etc. in milliseconds.
#define CAMERA_SETTLE_TIME       1000
struct stat st = {0};


int spi_im_w, spi_im_h, spi_im_jpeg_quality;
int GPIO_TO_WIRING_PI_MAP[]= {30, 31, 8, 9, 7, 21, 22, 11, 10, 13, 12, 14, 26, 23, 15, 16, 27, 0, 1, 24, 28, 29, 3, 4, 5, 6, 25, 2};

#define CUSTOM_EXIF_KEY "EXIF.UserComment"
#define CUSTOM_EXIF_HEADER "ver,temp,hum,bat,lum,lat,lng,alt,lsy"
#define CUSTOM_EXIF_FORMAT "%s,%.1f,%.1f,%i,%.2f,%.5f,%.5f,%.1f,%s"
#define CUSTOM_EXIF_TEMPLATE CUSTOM_EXIF_KEY "=" CUSTOM_EXIF_HEADER "\n" CUSTOM_EXIF_FORMAT


/** Structure containing all state information for the current run
 */
typedef struct
{
//   RASPICOMMONSETTINGS_PARAMETERS common_settings;     /// Common settings
   char camera_name[MMAL_PARAMETER_CAMERA_INFO_MAX_STR_LEN]; // Name of the camera sensor

   struct tm *timeinfo;
   char *linkname;                     /// filename of output file

     float temp; //4
     float  hum; // 4
     int bat; // 4

     float alt; //4
     double lng; // 8
     double lat; // 8

    float lum;
    char last_sync[20];


   MMAL_FOURCC_T encoding;             /// Encoding to use for the output file.
   int restart_interval;               /// JPEG restart interval. 0 for none.
   RASPIPREVIEW_PARAMETERS preview_parameters;    /// Preview setup parameters
   RASPICAM_CAMERA_PARAMETERS camera_parameters; /// Camera setup parameters
   MMAL_COMPONENT_T *camera_component;    /// Pointer to the camera component
   MMAL_COMPONENT_T *encoder_component;   /// Pointer to the encoder component
   MMAL_COMPONENT_T *null_sink_component; /// Pointer to the null sink component
   MMAL_CONNECTION_T *preview_connection; /// Pointer to the connection from camera to preview
   MMAL_CONNECTION_T *encoder_connection; /// Pointer to the connection from camera to encoder
   MMAL_POOL_T *encoder_pool; /// Pointer to the pool of buffers used by encoder output port
} RASPISTILL_STATE;

/** Struct used to pass information in encoder port userdata to callback
 */
typedef struct
{
   FILE *file_handle;                   /// File handle to write buffer data to.
   VCOS_SEMAPHORE_T complete_semaphore; /// semaphore which is posted when we reach end of frame (indicates end of capture or fault)
   RASPISTILL_STATE *pstate;            /// pointer to our state in case required in callback
} PORT_USERDATA;

// function prototypes
static MMAL_STATUS_T   add_custom_exif_field(RASPISTILL_STATE *state);
static void logging_error( char * pattern, ...);
static void logging( char * pattern, ...);


/**
 * Assign a default set of parameters to the state passed in
 *
 * @param state Pointer to state structure to assign defaults to
 */

static void default_status(RASPISTILL_STATE *state, struct tm *timeinfo)
{
   if (!state)
   {
      vcos_assert(0);
      return;
   }
   memset(state, 0, sizeof(*state));
   strncpy(state->camera_name, "(Unknown)", MMAL_PARAMETER_CAMERA_INFO_MAX_STR_LEN);


    state->temp=-300;
    state->hum -1;
    state->bat = -1;
    state->lum = 0.0;
    state->lat = 0.0;
    state->lng = 0.0;
    state->alt = 0.0;
    strcpy(state->last_sync, "2000-01-01 00:00:00");

   state->timeinfo = timeinfo;
   state->linkname = NULL;
   state->camera_component = NULL;
   state->encoder_component = NULL;
   state->preview_connection = NULL;
   state->encoder_connection = NULL;
   state->encoder_pool = NULL;
   state->encoding = MMAL_ENCODING_JPEG;

   // Setup preview window defaults
   state->preview_parameters.wantFullScreenPreview = 0;
   state->preview_parameters.preview_component = NULL;
   state->preview_parameters.display_num = -1;

   //fixme zoom defaults!


   raspicamcontrol_set_defaults(&state->camera_parameters);
}

/**
 * Dump image state parameters to stderr. Used for debugging
 *
 * @param state Pointer to state structure to assign defaults to
 */
static void dump_status(RASPISTILL_STATE *state)
{
   int i;

   if (!state)
   {
      vcos_assert(0);
      return;
   }


   fprintf(stderr, "Link to latest frame enabled ");
   if (state->linkname)
   {
      fprintf(stderr, " yes, -> %s\n", state->linkname);
   }
   else
   {
      fprintf(stderr, " no\n");
   }
   fprintf(stderr, "\n\n");

   raspicamcontrol_dump_parameters(&state->camera_parameters);
}

static void encoder_buffer_callback(MMAL_PORT_T *port, MMAL_BUFFER_HEADER_T *buffer)
{
   int complete = 0;

   // We pass our file handle and other stuff in via the userdata field.

   PORT_USERDATA *pData = (PORT_USERDATA *)port->userdata;

   if (pData)
   {
      int bytes_written = buffer->length;

      if (buffer->length && pData->file_handle)
      {
         mmal_buffer_header_mem_lock(buffer);

         bytes_written = fwrite(buffer->data, 1, buffer->length, pData->file_handle);

         mmal_buffer_header_mem_unlock(buffer);
      }

      // We need to check we wrote what we wanted - it's possible we have run out of storage.
      if (bytes_written != buffer->length)
      {
         vcos_log_error("Unable to write buffer to file - aborting");
         complete = 1;
      }

      // Now flag if we have completed
      if (buffer->flags & (MMAL_BUFFER_HEADER_FLAG_FRAME_END | MMAL_BUFFER_HEADER_FLAG_TRANSMISSION_FAILED))
         complete = 1;
   }
   else
   {
      vcos_log_error("Received a encoder buffer callback with no state");
   }

   // release buffer back to the pool
   mmal_buffer_header_release(buffer);

   // and send one back to the port (if still open)
   if (port->is_enabled)
   {
      MMAL_STATUS_T status = MMAL_SUCCESS;
      MMAL_BUFFER_HEADER_T *new_buffer;

      new_buffer = mmal_queue_get(pData->pstate->encoder_pool->queue);

      if (new_buffer)
      {
         status = mmal_port_send_buffer(port, new_buffer);
      }
      if (!new_buffer || status != MMAL_SUCCESS)
         vcos_log_error("Unable to return a buffer to the encoder port");
   }

   if (complete)
      vcos_semaphore_post(&(pData->complete_semaphore));
}

/**
 * Create the camera component, set up its ports
 *
 * @param state Pointer to state control struct. camera_component member set to the created camera_component if successful.
 *
 * @return MMAL_SUCCESS if all OK, something else otherwise
 *
 */
static MMAL_STATUS_T create_camera_component(RASPISTILL_STATE *state)
{
   MMAL_COMPONENT_T *camera = 0;
   MMAL_ES_FORMAT_T *format;
   MMAL_PORT_T *preview_port = NULL, *video_port = NULL, *still_port = NULL;
   MMAL_STATUS_T status;

   /* Create the component */
   status = mmal_component_create(MMAL_COMPONENT_DEFAULT_CAMERA, &camera);

   if (status != MMAL_SUCCESS)
   {
      vcos_log_error("Failed to create camera component");
      goto error;
   }

   status = raspicamcontrol_set_stereo_mode(camera->output[0], &state->camera_parameters.stereo_mode);
   status += raspicamcontrol_set_stereo_mode(camera->output[1], &state->camera_parameters.stereo_mode);
   status += raspicamcontrol_set_stereo_mode(camera->output[2], &state->camera_parameters.stereo_mode);

   if (status != MMAL_SUCCESS)
   {
      vcos_log_error("Could not set stereo mode : error %d", status);
      goto error;
   }

   MMAL_PARAMETER_INT32_T camera_num =
   {{MMAL_PARAMETER_CAMERA_NUM, sizeof(camera_num)}, CAMERA_NUM};

   status = mmal_port_parameter_set(camera->control, &camera_num.hdr);

   if (status != MMAL_SUCCESS)
   {
      vcos_log_error("Could not select camera : error %d", status);
      goto error;
   }

   if (!camera->output_num)
   {
      status = MMAL_ENOSYS;
      vcos_log_error("Camera doesn't have output ports");
      goto error;
   }

   status = mmal_port_parameter_set_uint32(camera->control, MMAL_PARAMETER_CAMERA_CUSTOM_SENSOR_CONFIG, SENSOR_MODE);

   if (status != MMAL_SUCCESS)
   {
      vcos_log_error("Could not set sensor mode : error %d", status);
      goto error;
   }

   preview_port = camera->output[MMAL_CAMERA_PREVIEW_PORT];
   video_port = camera->output[MMAL_CAMERA_VIDEO_PORT];
   still_port = camera->output[MMAL_CAMERA_CAPTURE_PORT];

   // Enable the camera, and tell it its control callback function
   status = mmal_port_enable(camera->control, default_camera_control_callback);

   if (status != MMAL_SUCCESS)
   {
      vcos_log_error("Unable to enable control port : error %d", status);
      goto error;
   }

   //  set up the camera configuration
   {
      MMAL_PARAMETER_CAMERA_CONFIG_T cam_config =
      {
         { MMAL_PARAMETER_CAMERA_CONFIG, sizeof(cam_config) },
         .max_stills_w = spi_im_w,
         .max_stills_h = spi_im_h,
         .stills_yuv422 = 0,
         .one_shot_stills = 1,
         .max_preview_video_w = 0,
         .max_preview_video_h = 0,
         .num_preview_video_frames = 3,
         .stills_capture_circular_buffer_height = 0,
         .fast_preview_resume = 0,
         .use_stc_timestamp = MMAL_PARAM_TIMESTAMP_MODE_RESET_STC
      };


     cam_config.max_preview_video_w = spi_im_w;
     cam_config.max_preview_video_h = spi_im_h;


      mmal_port_parameter_set(camera->control, &cam_config.hdr);
   }

   raspicamcontrol_set_all_parameters(camera, &state->camera_parameters);

   // Now set up the port formats

   format = preview_port->format;
   format->encoding = MMAL_ENCODING_OPAQUE;
   format->encoding_variant = MMAL_ENCODING_I420;

   if(state->camera_parameters.shutter_speed > 6000000)
   {
      MMAL_PARAMETER_FPS_RANGE_T fps_range = {{MMAL_PARAMETER_FPS_RANGE, sizeof(fps_range)},
         { 5, 1000 }, {166, 1000}
      };
      mmal_port_parameter_set(preview_port, &fps_range.hdr);
   }
   else if(state->camera_parameters.shutter_speed > 1000000)
   {
      MMAL_PARAMETER_FPS_RANGE_T fps_range = {{MMAL_PARAMETER_FPS_RANGE, sizeof(fps_range)},
         { 166, 1000 }, {999, 1000}
      };
      mmal_port_parameter_set(preview_port, &fps_range.hdr);
   }
      // In this mode we are forcing the preview to be generated from the full capture resolution.
      // This runs at a max of 15fps with the OV5647 sensor.
      format->es->video.width = VCOS_ALIGN_UP(spi_im_w, 32);
      format->es->video.height = VCOS_ALIGN_UP(spi_im_h, 16);
      format->es->video.crop.x = 0;
      format->es->video.crop.y = 0;
      format->es->video.crop.width = spi_im_w;
      format->es->video.crop.height = spi_im_h;
      format->es->video.frame_rate.num = FULL_RES_PREVIEW_FRAME_RATE_NUM;
      format->es->video.frame_rate.den = FULL_RES_PREVIEW_FRAME_RATE_DEN;


   status = mmal_port_format_commit(preview_port);
   if (status != MMAL_SUCCESS)
   {
      vcos_log_error("camera viewfinder format couldn't be set");
      goto error;
   }

   // Set the same format on the video  port (which we don't use here)
   mmal_format_full_copy(video_port->format, format);
   status = mmal_port_format_commit(video_port);

   if (status  != MMAL_SUCCESS)
   {
      vcos_log_error("camera video format couldn't be set");
      goto error;
   }

   // Ensure there are enough buffers to avoid dropping frames
   if (video_port->buffer_num < VIDEO_OUTPUT_BUFFERS_NUM)
      video_port->buffer_num = VIDEO_OUTPUT_BUFFERS_NUM;

   format = still_port->format;

   if(state->camera_parameters.shutter_speed > 6000000)
   {
      MMAL_PARAMETER_FPS_RANGE_T fps_range = {{MMAL_PARAMETER_FPS_RANGE, sizeof(fps_range)},
         { 5, 1000 }, {166, 1000}
      };
      mmal_port_parameter_set(still_port, &fps_range.hdr);
   }
   else if(state->camera_parameters.shutter_speed > 1000000)
   {
      MMAL_PARAMETER_FPS_RANGE_T fps_range = {{MMAL_PARAMETER_FPS_RANGE, sizeof(fps_range)},
         { 167, 1000 }, {999, 1000}
      };
      mmal_port_parameter_set(still_port, &fps_range.hdr);
   }
   // Set our stills format on the stills (for encoder) port
   format->encoding = MMAL_ENCODING_OPAQUE;
   format->es->video.width = VCOS_ALIGN_UP(spi_im_w, 32);
   format->es->video.height = VCOS_ALIGN_UP(spi_im_h, 16);
   format->es->video.crop.x = 0;
   format->es->video.crop.y = 0;
   format->es->video.crop.width = spi_im_w;
   format->es->video.crop.height = spi_im_h;
   format->es->video.frame_rate.num = STILLS_FRAME_RATE_NUM;
   format->es->video.frame_rate.den = STILLS_FRAME_RATE_DEN;

   status = mmal_port_format_commit(still_port);

   if (status != MMAL_SUCCESS)
   {
      vcos_log_error("camera still format couldn't be set");
      goto error;
   }

   /* Ensure there are enough buffers to avoid dropping frames */
   if (still_port->buffer_num < VIDEO_OUTPUT_BUFFERS_NUM)
      still_port->buffer_num = VIDEO_OUTPUT_BUFFERS_NUM;

   /* Enable component */
   status = mmal_component_enable(camera);

   if (status != MMAL_SUCCESS)
   {
      vcos_log_error("camera component couldn't be enabled");
      goto error;
   }

   state->camera_component = camera;
   return status;

error:

   if (camera)
      mmal_component_destroy(camera);

   return status;
}

/**
 * Destroy the camera component
 *
 * @param state Pointer to state control struct
 *
 */
static void destroy_camera_component(RASPISTILL_STATE *state)
{
   if (state->camera_component)
   {
      mmal_component_destroy(state->camera_component);
      state->camera_component = NULL;
   }
}

/**
 * Create the encoder component, set up its ports
 *
 * @param state Pointer to state control struct. encoder_component member set to the created camera_component if successful.
 *
 * @return a MMAL_STATUS, MMAL_SUCCESS if all OK, something else otherwise
 */
static MMAL_STATUS_T create_encoder_component(RASPISTILL_STATE *state)
{
   MMAL_COMPONENT_T *encoder = 0;
   MMAL_PORT_T *encoder_input = NULL, *encoder_output = NULL;
   MMAL_STATUS_T status;
   MMAL_POOL_T *pool;

   status = mmal_component_create(MMAL_COMPONENT_DEFAULT_IMAGE_ENCODER, &encoder);

   if (status != MMAL_SUCCESS)
   {
      vcos_log_error("Unable to create JPEG encoder component");
      goto error;
   }

   if (!encoder->input_num || !encoder->output_num)
   {
      status = MMAL_ENOSYS;
      vcos_log_error("JPEG encoder doesn't have input/output ports");
      goto error;
   }

   encoder_input = encoder->input[0];
   encoder_output = encoder->output[0];

   // We want same format on input and output
   mmal_format_copy(encoder_output->format, encoder_input->format);

   // Specify out output format
   encoder_output->format->encoding = state->encoding;

   encoder_output->buffer_size = encoder_output->buffer_size_recommended;

   if (encoder_output->buffer_size < encoder_output->buffer_size_min)
      encoder_output->buffer_size = encoder_output->buffer_size_min;

   encoder_output->buffer_num = encoder_output->buffer_num_recommended;

   if (encoder_output->buffer_num < encoder_output->buffer_num_min)
      encoder_output->buffer_num = encoder_output->buffer_num_min;

   // Commit the port changes to the output port
   status = mmal_port_format_commit(encoder_output);

   if (status != MMAL_SUCCESS)
   {
      vcos_log_error("Unable to set format on video encoder output port");
      goto error;
   }

   // Set the JPEG quality level
   status = mmal_port_parameter_set_uint32(encoder_output, MMAL_PARAMETER_JPEG_Q_FACTOR, spi_im_jpeg_quality);

   if (status != MMAL_SUCCESS)
   {
      vcos_log_error("Unable to set JPEG quality");
      goto error;
   }

   // Set the JPEG restart interval
   status = mmal_port_parameter_set_uint32(encoder_output, MMAL_PARAMETER_JPEG_RESTART_INTERVAL, state->restart_interval);

   if (state->restart_interval && status != MMAL_SUCCESS)
   {
      vcos_log_error("Unable to set JPEG restart interval");
      goto error;
   }

   // Set up any required thumbnail
   {
      MMAL_PARAMETER_THUMBNAIL_CONFIG_T param_thumb = {{MMAL_PARAMETER_THUMBNAIL_CONFIGURATION, sizeof(MMAL_PARAMETER_THUMBNAIL_CONFIG_T)}, 0, 0, 0, 0};
      status = mmal_port_parameter_set(encoder->control, &param_thumb.hdr);
   }

   //  Enable component
   status = mmal_component_enable(encoder);

   if (status  != MMAL_SUCCESS)
   {
      vcos_log_error("Unable to enable video encoder component");
      goto error;
   }

   /* Create pool of buffer headers for the output port to consume */
   pool = mmal_port_pool_create(encoder_output, encoder_output->buffer_num, encoder_output->buffer_size);

   if (!pool)
   {
      vcos_log_error("Failed to create buffer header pool for encoder output port %s", encoder_output->name);
   }

   state->encoder_pool = pool;
   state->encoder_component = encoder;
   return status;

error:

   if (encoder)
      mmal_component_destroy(encoder);

   return status;
}

/**
 * Destroy the encoder component
 *
 * @param state Pointer to state control struct
 *
 */
static void destroy_encoder_component(RASPISTILL_STATE *state)
{
   // Get rid of any port buffers first
   if (state->encoder_pool)
   {
      mmal_port_pool_destroy(state->encoder_component->output[0], state->encoder_pool);
   }

   if (state->encoder_component)
   {
      mmal_component_destroy(state->encoder_component);
      state->encoder_component = NULL;
   }
}


/**
 * Add an exif tag to the capture
 *
 * @param state Pointer to state control struct
 * @param exif_tag String containing a "key=value" pair.
 * @return  Returns a MMAL_STATUS_T giving result of operation
 */
static MMAL_STATUS_T add_exif_tag(RASPISTILL_STATE *state, const char *exif_tag)
{
   MMAL_STATUS_T status;
   int payload_length = MAX_EXIF_PAYLOAD_LENGTH;

   MMAL_PARAMETER_EXIF_T *exif_param = (MMAL_PARAMETER_EXIF_T*)calloc(sizeof(MMAL_PARAMETER_EXIF_T) + payload_length, 1);

   vcos_assert(state);
   vcos_assert(state->encoder_component);

   // Check to see if the tag is present or is indeed a key=value pair.
   if (!exif_tag || strchr(exif_tag, '=') == NULL || strlen(exif_tag) > payload_length-1){
      logging_error("Failed to save exif field: %s", exif_tag);
      return MMAL_EINVAL;
    }
   exif_param->hdr.id = MMAL_PARAMETER_EXIF;

   strncpy((char*)exif_param->data, exif_tag, payload_length-1);
   exif_param->hdr.size = sizeof(MMAL_PARAMETER_EXIF_T) + strlen((char*)exif_param->data);
   status = mmal_port_parameter_set(state->encoder_component->output[0], &exif_param->hdr);
   free(exif_param);

   return status;
}


static MMAL_STATUS_T  add_custom_exif_field(RASPISTILL_STATE *state){
    char path[64];
    char buffer[128] = "";
    struct stat attr;

    sprintf(path, "%s/%s", SPI_IMAGE_DIR, SPI_METADATA_FILENAME);
    if(stat(path, &attr) < 0){
        logging_error("No metadata file found!");
    }

    else{
        // parse metadata file should contain data like:
//        char file_buffer[512] = "{1}";
        char file_buffer[512] = "";
        int r;

        FILE *fp;
        fp = fopen (path, "r");
        fgets(file_buffer, 512-1, fp);
        fclose(fp);

        jsmn_parser p;
        jsmntok_t t[32]; /* We expect no more than 128 JSON tokens */

        jsmn_init(&p);
        r = jsmn_parse(&p, file_buffer, strlen(file_buffer), t, 32); // "s" is the char array holding the json content

        if(r <0 ||
            t[0].size == 0  // no children
            ){
            logging_error("Issues parsing json metadata: `%s'. Expect `{'a':1, ...}'", file_buffer);
        }

        else{
            unsigned int i;
            for(i=1; i != r; ++i){
                if(t[i].size != 1){
                    continue;
                }
                jsmntok_t key = t[i];

                unsigned int length = key.end - key.start;
                char key_string[length + 1];
                memcpy(key_string, &file_buffer[key.start], length);
                key_string[length] = '\0';

                jsmntok_t value = t[i+1];

                length = value.end - value.start;
                char value_string[length + 1];
                memcpy(value_string, &file_buffer[value.start], length);
                value_string[length] = '\0';
                if (strcmp(key_string, "lat") == 0){
                    state->lat = atof(value_string);
                }
                else if (strcmp(key_string, "lng") == 0){
                    state->lng = atof(value_string);
                }
                else if (strcmp(key_string, "alt") == 0){
                  state->alt = atof(value_string);
                }
                else if (strcmp(key_string, "datetime") == 0){
                    strcpy(state->last_sync, value_string);
                }
                else{
                    logging_error("Unexpected token in metadata: `%s:%s'", key_string, value_string);
                }
            }
            }
        }
    snprintf(buffer, 128,CUSTOM_EXIF_TEMPLATE,
        SPI_VERSION,
        state->temp,
        state->hum,
        state->bat,
        state->lum,
        state->lat,
        state->lng,
        state->alt,
        state->last_sync);
    return add_exif_tag(state, buffer);
}


/**
 * Add a basic set of EXIF tags to the capture
 * Make, Time etc
 *
 * @param state Pointer to state control struct
 *
 */
static void add_exif_tags(RASPISTILL_STATE *state)
{
   char model_buf[32];
   char time_buf[32];
   char exif_buf[128];
   int i;

   snprintf(model_buf, 32, "IFD0.Model=RP_%s", state->camera_name);
   add_exif_tag(state, model_buf);
   snprintf(model_buf, 32, "IFD0.Make=StickyPi");
   add_exif_tag(state, model_buf);
   snprintf(time_buf, sizeof(time_buf),
            "%04d:%02d:%02d %02d:%02d:%02d",
            state->timeinfo->tm_year+1900,
            state->timeinfo->tm_mon+1,
            state->timeinfo->tm_mday,
            state->timeinfo->tm_hour,
            state->timeinfo->tm_min,
            state->timeinfo->tm_sec);

   snprintf(exif_buf, sizeof(exif_buf), "EXIF.DateTimeDigitized=%s", time_buf);
   add_exif_tag(state, exif_buf);

   snprintf(exif_buf, sizeof(exif_buf), "EXIF.DateTimeOriginal=%s", time_buf);
   add_exif_tag(state, exif_buf);

   snprintf(exif_buf, sizeof(exif_buf), "IFD0.DateTime=%s", time_buf);
    add_exif_tag(state, exif_buf);

    add_custom_exif_field(state);
    }


/**
 * Allocates and generates a filename based on the
 * user-supplied pattern and the frame number.
 * On successful return, finalName and tempName point to malloc()ed strings
 * which must be freed externally.  (On failure, returns nulls that
 * don't need free()ing.)
 *
 * @param finalName pointer receives an
 * @param pattern sprintf pattern with %d to be replaced by frame
 * @param frame for timelapse, the frame number
 * @return Returns a MMAL_STATUS_T giving result of operation
*/

MMAL_STATUS_T create_filenames(char** finalName, char** tempName, char * pattern)
{
   *finalName = NULL;
   *tempName = NULL;

   if (0 > asprintf(finalName, pattern) ||
         0 > asprintf(tempName, "%s~", *finalName))
   {
      if (*finalName != NULL)
      {
         free(*finalName);
      }
      return MMAL_ENOMEM;    // It may be some other error, but it is not worth getting it right
   }
   return MMAL_SUCCESS;
}


static void rename_file(RASPISTILL_STATE *state, FILE *output_file,
                        const char *final_filename, const char *use_filename)
{
   MMAL_STATUS_T status;

   fclose(output_file);
   vcos_assert(use_filename != NULL && final_filename != NULL);
   if (0 != rename(use_filename, final_filename))
   {
      vcos_log_error("Could not rename temp file to: %s; %s",
                     final_filename,strerror(errno));
   }
   if (state->linkname)
   {
      char *use_link;
      char *final_link;
      status = create_filenames(&final_link, &use_link, state->linkname);

      // Create hard link if possible, symlink otherwise
      if (status != MMAL_SUCCESS
            || (0 != link(final_filename, use_link)
                &&  0 != symlink(final_filename, use_link))
            || 0 != rename(use_link, final_link))
      {
         vcos_log_error("Could not link as filename: %s; %s",
                        state->linkname,strerror(errno));
      }
      if (use_link) free(use_link);
      if (final_link) free(final_link);
   }
}


static void set_device_id(char *device_id){
    FILE *fp = fopen("/proc/cpuinfo", "r");
    assert(fp != NULL);
    size_t n = 0;
    char *line = NULL;
    char first_six_char[6+1] = "";
    char match_word[] = "Serial";

    while (getline(&line, &n, fp) > 0) {
            strncpy(first_six_char, line, 6);
            if(strcmp(first_six_char, match_word) == 0){
                strncpy(device_id, line + 18, 8);
            }
    }
    free(line);
    fclose(fp);

}
static void * set_picture_path(struct tm *timeinfo, char *picture_path){
    char device_name[8+1] = "";
    char datetime_str[32] = "";
    char time_buf[32] = "";
//    memset (device_name,'\0',9);

   set_device_id(device_name);
   if(device_name[0] == '\0'){
        logging_error("Cannot set device name!");
   }

   snprintf(datetime_str, sizeof(time_buf),
            "%04d-%02d-%02d_%02d-%02d-%02d",
            timeinfo->tm_year+1900,
            timeinfo->tm_mon+1,
            timeinfo->tm_mday,
            timeinfo->tm_hour,
            timeinfo->tm_min,
            timeinfo->tm_sec);

    snprintf(picture_path,128, "%s/%s",SPI_IMAGE_DIR, device_name);
    if (stat(picture_path, &st) == -1){
        mkdir(picture_path, 0755);
    }
    snprintf(picture_path,128, "%s/%s/%s.%s.jpg",SPI_IMAGE_DIR, device_name, device_name ,datetime_str);
}

static void logging( char * pattern, ...){
    printf("INFO:  ");
   va_list args;
    va_start(args, pattern);
    vprintf(pattern, args);
    va_end(args);
    printf("\n");
    fflush(stdout);
}

static void logging_error( char * pattern, ...){
    fprintf(stderr, "ERROR: ");
    va_list args;
    va_start(args, pattern);
    vfprintf(stderr, pattern, args);
    va_end(args);
    fprintf(stderr, "\n");
    fflush(stderr);
}


/**
 * main
 */

static void read_dht_and_sleep(RASPISTILL_STATE * state){

    DHT_DATA dht_data = {-300.0, -1.0};
    int status;
    struct timeval t0, t1, delta_t;
    gettimeofday(&t0, NULL);
    status = dht_read_data(&dht_data, 0);
    gettimeofday(&t1, NULL);
    timersub(&t1, &t0, &delta_t);

    int time_to_sleep = CAMERA_SETTLE_TIME  - (unsigned long) (delta_t.tv_sec * 1000 + delta_t.tv_usec / 1000) ;

    // in case of weird overflow ... maybe overly defensive, but we really don't want to sleep forever
    if (time_to_sleep > CAMERA_SETTLE_TIME){
        time_to_sleep = CAMERA_SETTLE_TIME;
        }
    if (status == 0){
        logging("T, H = %02f, %02f\n", dht_data.temp, dht_data.hum);
        }
    else{
        logging_error("Failed to read DHT");
    }
    if(time_to_sleep >0){
        vcos_sleep(time_to_sleep);
        }
    state->temp = dht_data.temp;
    state->hum = dht_data.hum;
}

int read_gpio_once(int pin){
    pin = GPIO_TO_WIRING_PI_MAP[pin];
    pinMode(pin, INPUT);
    return digitalRead(pin);
}

int is_test_gpio_up(){
    read_gpio_once(atoi(SPI_TESTING_GPIO));
    }

int is_manual_on_gpio_up(){
    read_gpio_once(atoi(SPI_MANUAL_ON_GPIO));
    }

int must_try_to_sync() {
    char path[64];
    char touch_command[64];
    time_t last_run_time, now;
    struct stat attr;

    sprintf(path, "%s/%s", SPI_IMAGE_DIR, SPI_METADATA_FILENAME);

    if(stat(path, &attr) == 0){
        last_run_time = attr.st_mtime;
    }
    else{
        last_run_time = time(0);
        FILE *fp;
        fp = fopen (path, "w");
        fputs("{}", fp);
        fclose(fp);
    }

    sprintf(touch_command, "touch %s", path);
    system(touch_command);

    // to ensure we have no gap in time, time is only read from our metadata timetsamp file
    stat(path, &attr);
    now = attr.st_mtime;

    long sync_period_seconds = atoi(SPI_SYNC_PERIOD_MINUTES) * 60;
    time_t last_run_period = last_run_time /   sync_period_seconds;
    time_t  now_period = now /  sync_period_seconds;
    if(now_period > last_run_period){
        return 1;
    }
    return 0 ;
}




void read_battery_level(RASPISTILL_STATE *state){
// translated from https://stackoverflow.com/questions/24378430/reading-data-out-of-an-adc-mcp3001-with-python-spi works
    int gpio_11 = GPIO_TO_WIRING_PI_MAP[11];
    int gpio_8 = GPIO_TO_WIRING_PI_MAP[8];
    int gpio_9 = GPIO_TO_WIRING_PI_MAP[9];
    int gpio_6 = GPIO_TO_WIRING_PI_MAP[6];

//    GPIO.setup(11, GPIO.OUT)
    pinMode(gpio_11, OUTPUT);

//    GPIO.setup(8, GPIO.OUT)
    pinMode(gpio_8, OUTPUT);

//    GPIO.setup(9, GPIO.IN)
    pinMode(gpio_9, INPUT);

//    GPIO.output(11, False)  # CLK low
    digitalWrite(gpio_11,LOW);

//    GPIO.output(6, False)   # /CS low
    digitalWrite(gpio_6,LOW);

    int adcvalue = 0;
    int i;
    int input_val;
    for(i=0; i != 13; ++i){
//        GPIO.output(11, True)
        digitalWrite(gpio_11,HIGH);
//        GPIO.output(11, False)
        digitalWrite(gpio_11,LOW);
        adcvalue <<= 1;
        input_val = digitalRead(gpio_9);
//        if(GPIO.input(9)):
        if(input_val){
            adcvalue |= 0x001;
        }
    }
//            adcvalue |= 0x001
    digitalWrite(gpio_6, HIGH);
    adcvalue &= 0x3ff;
    state->bat = (int) (100.0 * ((float) adcvalue / 1024.0));

}


void calc_lum(RASPISTILL_STATE *state, MMAL_COMPONENT_T *camera)
{
//    MMAL_PARAMETER_INPUT_CROP_T crop;
   MMAL_PARAMETER_CAMERA_SETTINGS_T settings;


   settings.hdr.id = MMAL_PARAMETER_CAMERA_SETTINGS;
   settings.hdr.size = sizeof(settings);

   if (mmal_port_parameter_get(camera->control, &settings.hdr) != MMAL_SUCCESS){
        logging_error("Issue reading camera settings");
        return;
   }
//   logging("%f,  %f,", settings.analog_gain, settings.digital_gain);
   state->lum = log10(1e6 / settings.exposure);

}



int main(int argc, const char **argv)
{

    spi_im_w =atoi(SPI_IM_W);
    spi_im_h = atoi(SPI_IM_H);
    spi_im_jpeg_quality = atoi(SPI_IM_JPEG_QUALITY);
    char filename[128] = "";
    time_t rawtime;
    struct tm * timeinfo;

    time(&rawtime);
    timeinfo = localtime(&rawtime);
    set_picture_path(timeinfo, filename);
    logging("Taking picture to file %s", filename);

    if (wiringPiSetup() == -1) {
        logging_error("Failed to initialize wiringPi\n");
	}
    else if (is_test_gpio_up()){
        logging("Testing bridge is on, entering testing mode");
        return atoi(SPI_TAKE_PICTURE_TESTING_STATUS);
    }

    int was_turned_on_by_button = is_manual_on_gpio_up();
    int periodic_sync_attempt = must_try_to_sync();
    // highest priority for this program.
    // maybe helps with time sensitive operations such as reading
    // sensors at the software level
   piHiPri(99);

   // Our main data storage vessel..
   RASPISTILL_STATE state;
   int exit_code = EX_OK;

   MMAL_STATUS_T status = MMAL_SUCCESS;
   MMAL_PORT_T *camera_preview_port = NULL;
   MMAL_PORT_T *camera_video_port = NULL;
   MMAL_PORT_T *camera_still_port = NULL;
   MMAL_PORT_T *preview_input_port = NULL;
   MMAL_PORT_T *encoder_input_port = NULL;
   MMAL_PORT_T *encoder_output_port = NULL;

   bcm_host_init();

   // Register our application with the logging system
   vcos_log_register("RaspiStill", VCOS_LOG_CATEGORY);

   signal(SIGINT, default_signal_handler);

   // Disable USR1 and USR2 for the moment - may be reenabled if go in to signal capture mode
   signal(SIGUSR1, SIG_IGN);
   signal(SIGUSR2, SIG_IGN);

   set_app_name(argv[0]);
   default_status(&state, timeinfo);
   // Setup for sensor specific parameters
   get_sensor_defaults(CAMERA_NUM, state.camera_name);


   // OK, we have a nice set of parameters. Now set up our components
   // We have three components. Camera, Preview and encoder.
   // Camera and encoder are different in stills/video, but preview
   // is the same so handed off to a separate module

   if ((status = create_camera_component(&state)) != MMAL_SUCCESS)
   {
      vcos_log_error("%s: Failed to create camera component", __func__);
      exit_code = EX_SOFTWARE;
   }
   else if ((status = raspipreview_create(&state.preview_parameters)) != MMAL_SUCCESS)
   {
      vcos_log_error("%s: Failed to create preview component", __func__);
      destroy_camera_component(&state);
      exit_code = EX_SOFTWARE;
   }
   else if ((status = create_encoder_component(&state)) != MMAL_SUCCESS)
   {
      vcos_log_error("%s: Failed to create encode component", __func__);
      raspipreview_destroy(&state.preview_parameters);
      destroy_camera_component(&state);
      exit_code = EX_SOFTWARE;
   }
   else
   {
      PORT_USERDATA callback_data;

      camera_preview_port = state.camera_component->output[MMAL_CAMERA_PREVIEW_PORT];
      camera_video_port   = state.camera_component->output[MMAL_CAMERA_VIDEO_PORT];
      camera_still_port   = state.camera_component->output[MMAL_CAMERA_CAPTURE_PORT];
      encoder_input_port  = state.encoder_component->input[0];
      encoder_output_port = state.encoder_component->output[0];

     // Note we are lucky that the preview and null sink components use the same input port
     // so we can simple do this without conditionals
     preview_input_port  = state.preview_parameters.preview_component->input[0];

     // Connect camera to preview (which might be a null_sink if no preview required)
     status = connect_ports(camera_preview_port, preview_input_port, &state.preview_connection);


      if (status == MMAL_SUCCESS)
      {
         VCOS_STATUS_T vcos_status;

         // Now connect the camera to the encoder
         status = connect_ports(camera_still_port, encoder_input_port, &state.encoder_connection);

         if (status != MMAL_SUCCESS)
         {
            vcos_log_error("%s: Failed to connect camera video port to encoder input", __func__);
            goto error;
         }

         // Set up our userdata - this is passed though to the callback where we need the information.
         // Null until we open our filename
         callback_data.file_handle = NULL;
         callback_data.pstate = &state;
         vcos_status = vcos_semaphore_create(&callback_data.complete_semaphore, "RaspiStill-sem", 0);

         vcos_assert(vcos_status == VCOS_SUCCESS);

         if (status != MMAL_SUCCESS)
         {
            vcos_log_error("Failed to setup encoder output");
            goto error;
         }

         else
         {

        FILE *output_file = NULL;
        char *use_filename = NULL;      // Temporary filename while image being written
        char *final_filename = NULL;    // Name that file gets once writing complete

        int i=0;
        MMAL_PARAMETER_CAMERA_SETTINGS_T settings;


        // we wait for camera to warmup. meanwhile, we read DHT

        read_dht_and_sleep(&state);
        read_battery_level(&state);
        calc_lum(&state, state.camera_component);
         vcos_assert(use_filename == NULL && final_filename == NULL);
         status = create_filenames(&final_filename, &use_filename, filename);
         if (status  != MMAL_SUCCESS)
         {
            vcos_log_error("Unable to create filenames");
            goto error;
         }
         // Technically it is opening the temp~ filename which will be renamed to the final filename

         output_file = fopen(use_filename, "wb");

         if (!output_file)
         {
            // Notify user, carry on but discarding encoded output buffers
            vcos_log_error("%s: Error opening output file: %s\nNo output file will be generated\n", __func__, use_filename);
         }

          callback_data.file_handle = output_file;

          add_exif_tags(&state);

          // There is a possibility that shutter needs to be set each loop.
          if (mmal_status_to_int(mmal_port_parameter_set_uint32(state.camera_component->control, MMAL_PARAMETER_SHUTTER_SPEED, state.camera_parameters.shutter_speed)) != MMAL_SUCCESS)
             vcos_log_error("Unable to set shutter speed");


          // Enable the encoder output port
          encoder_output_port->userdata = (struct MMAL_PORT_USERDATA_T *)&callback_data;


          // Enable the encoder output port and tell it its callback function
          status = mmal_port_enable(encoder_output_port, encoder_buffer_callback);

          int num, q;
          // Send all the buffers to the encoder output port
          num = mmal_queue_length(state.encoder_pool->queue);


          for (q=0; q<num; q++)
          {
             MMAL_BUFFER_HEADER_T *buffer = mmal_queue_get(state.encoder_pool->queue);

             if (!buffer)
                vcos_log_error("Unable to get a required buffer %d from pool queue", q);

             if (mmal_port_send_buffer(encoder_output_port, buffer)!= MMAL_SUCCESS)
                vcos_log_error("Unable to send a buffer to encoder output port (%d)", q);
          }



          if (mmal_port_parameter_set_boolean(camera_still_port, MMAL_PARAMETER_CAPTURE, 1) != MMAL_SUCCESS)
          {
             vcos_log_error("%s: Failed to start capture", __func__);
          }
          else
          {
             // Wait for capture to complete
             // For some reason using vcos_semaphore_wait_timeout sometimes returns immediately with bad parameter error
             // even though it appears to be all correct, so reverting to untimed one until figure out why its erratic
             vcos_semaphore_wait(&callback_data.complete_semaphore);
          }

          // Ensure we don't die if get callback with no open file
          callback_data.file_handle = NULL;

          if (output_file != stdout)
          {
             rename_file(&state, output_file, final_filename, use_filename);
          }
          else
          {
             fflush(output_file);
          }
          // Disable encoder output port
          status = mmal_port_disable(encoder_output_port);


           if (use_filename)
           {
              free(use_filename);
              use_filename = NULL;
           }
           if (final_filename)
           {
              free(final_filename);
              final_filename = NULL;
           }
            vcos_semaphore_delete(&callback_data.complete_semaphore);
         }
      }
      else
      {
         mmal_status_to_int(status);
         vcos_log_error("%s: Failed to connect camera to preview", __func__);
      }

      logging("Success saving %s", filename);
error:

      mmal_status_to_int(status);

      // Disable all our ports that are not handled by connections
      check_disable_port(camera_video_port);
      check_disable_port(encoder_output_port);

      if (state.preview_connection)
         mmal_connection_destroy(state.preview_connection);

      if (state.encoder_connection)
         mmal_connection_destroy(state.encoder_connection);

      /* Disable components */
      if (state.encoder_component)
         mmal_component_disable(state.encoder_component);

      if (state.preview_parameters.preview_component)
         mmal_component_disable(state.preview_parameters.preview_component);

      if (state.camera_component)
         mmal_component_disable(state.camera_component);

      destroy_encoder_component(&state);
      raspipreview_destroy(&state.preview_parameters);
      destroy_camera_component(&state);
   }

    if (status != MMAL_SUCCESS)
        raspicamcontrol_check_configuration(128);

   //else we turn off!
   char command_buffer[64]="";
   char flag[4]="";

    if(was_turned_on_by_button){
        logging("Device manually turned on");
        strcpy(flag,"-u");
    }
    else if(periodic_sync_attempt){
        logging("Periodic syncing attempt");
        strcpy(flag,"-p");
    }

    else{
        logging("Not syncing");
        }

    sprintf(command_buffer, "%s -b %i %s", "sync_to_harvester.py", state.bat, flag);

    if(strlen(flag) >0)
        system(command_buffer);

    // the turnoff process
    system("sync");
    int spi_off_gpio =   atoi(SPI_OFF_GPIO);
    int off_pin = GPIO_TO_WIRING_PI_MAP[spi_off_gpio];
    pinMode(off_pin, OUTPUT);
    //digitalWrite(off_pin, HIGH);

    return exit_code;
}

