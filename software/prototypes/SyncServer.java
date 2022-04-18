

public class SyncServer {
  public static void main(String[] args){
    int port = 9000;
    HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);
    System.out.println("server started at " + port);
    server.createContext("/", new RootHandler());
    server.createContext("/echoHeader", new EchoHeaderHandler());
    server.createContext("/echoGet", new EchoGetHandler());
    server.createContext("/echoPost", new EchoPostHandler());
    server.setExecutor(null);
    server.start();
  }//End of main
}//End of FirstJavaProgram Class
