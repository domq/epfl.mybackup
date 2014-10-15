package ch.epfl.mybackup.vm;

import ch.epfl.mybackup.beans.Server;
import ch.epfl.mybackup.beans.Container;
import java.util.ArrayList;

import java.io.*;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;



import org.apache.commons.io.IOUtils;

@Component("MainVM")
@Scope("desktop")
public class MainVM implements java.io.Serializable{

	static Logger log = LoggerFactory.getLogger(MainVM.class.getName());

	public Server getServer() throws IOException{
		String serverData= getServerData();
		Server server=new flexjson.JSONDeserializer<Server>().deserialize(serverData);
		return server;
	}

	public String getServerData()  throws IOException{
		InputStream in = this.getClass().getClassLoader()
                                .getResourceAsStream("serverData.json");
		return IOUtils.toString(in,"utf-8");
	}
}
