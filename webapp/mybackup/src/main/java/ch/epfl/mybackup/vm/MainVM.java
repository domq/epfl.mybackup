package ch.epfl.mybackup.vm;

import ch.epfl.mybackup.beans.Server;
import ch.epfl.mybackup.beans.Container;
import ch.epfl.mybackup.service.MessageService;

import java.util.ArrayList;

import java.io.*;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;
import org.springframework.context.annotation.PropertySource;
import org.springframework.context.annotation.Configuration;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.beans.factory.annotation.Autowired;

import org.apache.commons.lang3.StringUtils;

import org.apache.commons.io.IOUtils;

@Component("MainVM")
@Scope("desktop")
@Configuration
@PropertySource("classpath:system.properties")
public class MainVM implements java.io.Serializable{

	@Autowired
	MessageService mService;

	static Logger log = LoggerFactory.getLogger(MainVM.class.getName());

	public Server getServer() throws IOException{
// 		String serverData= getServerData();
		String serverData=mService.getServerData();
		if (StringUtils.isEmpty(serverData)) return null;
		else{
			Server server=new flexjson.JSONDeserializer<Server>().deserialize(serverData);
			return server;
		}
	}


	public String getServerData()  throws IOException{
		InputStream in = this.getClass().getClassLoader()
                                .getResourceAsStream("serverData.json");
		return IOUtils.toString(in,"utf-8");
	}
}
