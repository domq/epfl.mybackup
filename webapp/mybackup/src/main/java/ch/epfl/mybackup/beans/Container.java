package ch.epfl.mybackup.beans;

import java.util.List;
import lombok.Data;

@Data
public class Container {
	private String name;
	private String state;
	private List<IpForward> ipForwards;
}