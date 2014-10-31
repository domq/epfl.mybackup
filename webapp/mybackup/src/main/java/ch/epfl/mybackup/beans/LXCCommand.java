package ch.epfl.mybackup.beans;

import java.util.List;
import lombok.Data;
import lombok.EqualsAndHashCode;



@Data
@EqualsAndHashCode
public class LXCCommand {
	public static String START_CONTAINER="start_container";
	public LXCCommand(String destinationTopic, String command, String ... parameters){
		this.topic=destinationTopic;
		this.command=command;
		this.parameters=parameters;
	}
	String topic;
	String command;
	String [] parameters;
}