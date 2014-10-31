package ch.epfl.mybackup.beans;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.Date;

import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode
public class Server{
	private List<Container> containers;
	private String hostIP;
	private String hostname;
	private String version;
}