package ch.epfl.mybackup.beans;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;

public class Server{
	private List<Map<String,Container>> containers;
	private String hostIP;
	private String hostname;
	public List<Container> getContainers(){
		ArrayList<Container> realcontainers=new ArrayList<Container>();
		for (Map map : containers){
			realcontainers.add(map.values().iterator().next());
		}
		return realcontainers;
	}
	public String getHostIP(){
		return hostIP;
	}
	public String getHostname(){
		return hostname;
	}

}