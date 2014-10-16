package ch.epfl.mybackup.service;

import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;

import org.springframework.context.annotation.PropertySource;
import org.springframework.context.annotation.Configuration;
import org.springframework.beans.factory.annotation.Value;



import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import org.springframework.beans.factory.annotation.Autowired;


import org.springframework.amqp.core.Message;
import org.springframework.amqp.core.MessageListener;

import lombok.Getter;
import lombok.Setter;




@Component("MessageService")
@Scope("singleton")
public class MessageService implements MessageListener{

	
	@Getter @Setter String serverData;
	
	@PostConstruct
	public void init(){
		  System.err.println("Mesage service intitialized");
	}

	public void onMessage(Message message) {
        System.err.println("Received <" + message.getBody() + ">");
		serverData=new String(message.getBody());
    }
}