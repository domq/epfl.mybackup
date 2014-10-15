package ch.epfl.mybackup.beans;
import lombok.Data;

@Data
public class IpForward{
	private String dest;
	private String source;
	private Integer port;
	private String protocol;
}
