package ch.epfl.mybackup.service;

import java.util.Date;

import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;

import org.springframework.context.annotation.PropertySource;
import org.springframework.context.annotation.Configuration;
import org.springframework.beans.factory.annotation.Value;

import org.apache.log4j.Logger;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import org.springframework.beans.factory.annotation.Autowired;

import org.springframework.amqp.rabbit.annotation.*;
import org.springframework.amqp.rabbit.core.RabbitTemplate;


import lombok.Getter;
import lombok.Setter;




@Component("MessageService")
@Scope("singleton")
public class MessageService{

	static Logger log = Logger.getLogger(MessageService.class.getName());
	
	@Getter String serverData;
	@Getter Date lastUpdate;

	@Autowired
	RabbitTemplate sender;
	
	@PostConstruct
	public void init(){
		  log.debug("Mesage service intitialized");
	}

	@RabbitListener(queues="masterQueueWebserverDev", containerFactory="myListenerContainerFactory",admin="myContainerAdmin")
	public void messageReceived(byte[] message) throws java.io.UnsupportedEncodingException{
        log.error("Received <" + message + ">");
		serverData=new String(message,"UTF-8");
		lastUpdate=new java.util.Date();
    }

	public void sendMessage(String topic, String message){
		sender.convertAndSend(topic, message);
	}

	
}