package ch.epfl.mybackup;

import ch.epfl.mybackup.beans.*;
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

	public Server getServerData() throws IOException{
		InputStream in = this.getClass().getClassLoader()
                                .getResourceAsStream("serverData.json");
		String serverData= IOUtils.toString(in,"utf-8");
		Server server=new flexjson.JSONDeserializer<Server>().deserialize(serverData,Server.class);
		return server;
	}
}
