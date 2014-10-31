package ch.epfl.mybackup.beans;

import java.util.List;
import lombok.Data;
import lombok.EqualsAndHashCode;



@Data
@EqualsAndHashCode
public class Container {
	private String name;
	private String state;
	private String MAC;
	private String IPv4;
	private List<IpForward> ipForwards;
	private String version;

}