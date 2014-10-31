package ch.epfl.mybackup.vm;

import ch.epfl.mybackup.beans.*;
import ch.epfl.mybackup.service.*;

import java.util.ArrayList;
import java.util.List;

import java.io.*;

import org.apache.log4j.Logger;

import java.util.Date;


import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;
import org.springframework.context.annotation.PropertySource;
import org.springframework.context.annotation.Configuration;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.zkoss.bind.annotation.Command;
import org.zkoss.bind.annotation.NotifyChange;
import org.zkoss.zul.ListModelList;

import org.apache.commons.lang3.StringUtils;

import org.apache.commons.io.IOUtils;

import lombok.Getter;
import lombok.Setter;

//ZK
import org.zkoss.zk.ui.select.Selectors;
import org.zkoss.bind.annotation.*;
import org.zkoss.zk.ui.Desktop;
import org.zkoss.zk.ui.event.*;
import org.zkoss.bind.BindUtils;


import java.util.Collections;

@Component("MainVM")
@Scope("desktop")
public class MainVM implements java.io.Serializable{

	@Autowired MessageService mService;

	static Logger log = Logger.getLogger(MainVM.class.getName());

	private Server server;
	private flexjson.JSONSerializer serializer = new flexjson.JSONSerializer();

	@AfterCompose
	public void init(@ContextParam(ContextType.VIEW) org.zkoss.zk.ui.Component view,@ContextParam(ContextType.DESKTOP) Desktop _desktop){
		Selectors.wireComponents(view, this, false);
		Selectors.wireEventListeners(view, this);
	}

	public Server getServer() throws IOException{
		String serverData=mService.getServerData();
		log.debug(serverData);
		if (StringUtils.isEmpty(serverData)) return null;
		else{
			server= new flexjson.JSONDeserializer<Server>().deserialize(serverData);
			return server;
		}
	}

	public List<Container> getContainers() throws IOException{
		try{
			return server.getContainers();
		}catch(NullPointerException npe){
			return null;
		}
	}
	
	public Date getLastUpdate(){
		return mService.getLastUpdate();
	}

	@Command
	public void updateView() throws IOException{
		getServer();
	}

	@Command
	@NotifyChange({"server","lastUpdate"})
	public void updateServers(){
	}

	@Command
	public void startContainer(@BindingParam("servername") String servername, @BindingParam("container") Container container){
		log.error("container: "+container.getClass()+" starting");
		LXCCommand command=new LXCCommand("lxc.server."+servername,LXCCommand.START_CONTAINER,container.getName());
		String jsonCommand=serializer.exclude("class").include("parameters").serialize(command);
		mService.sendMessage(command.getTopic(),jsonCommand);
	}

	@Command
	public void stopContainer(@BindingParam("container") Container container){
		log.error("container: "+container.getClass()+" stopping");
	}

	@Command
	public void freezeContainer(@BindingParam("container") Container container){
		log.error("container: "+container.getClass()+" freezing");
	}

	@Command
	public void unfreezeContainer(@BindingParam("container") Container container){
		log.error("container: "+container.getClass()+" unfreezing");
	}

	@Command
	public void deleteIpForward(@BindingParam("ipforward") IpForward ipforward){
		log.error("deleting ipforward:"+ipforward);
	}

	public String getServerData()  throws IOException{
		InputStream in = this.getClass().getClassLoader()
                                .getResourceAsStream("serverData.json");
		return IOUtils.toString(in,"utf-8");
	}


}
