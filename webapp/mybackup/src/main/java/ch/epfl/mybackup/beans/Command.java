package ch.epfl.mybackup.beans;

import java.util.List;
import lombok.Data;
import lombok.EqualsAndHashCode;



@Data
@EqualsAndHashCode
public class Command {
	String destinationTopic;
	String command;
	String [] parameters;
}