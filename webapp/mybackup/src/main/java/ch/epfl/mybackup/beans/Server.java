package ch.epfl.mybackup.beans;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;

import lombok.Data;

@Data
public class Server{
	private List<Container> containers;
	private String hostIP;
	private String hostname;
}