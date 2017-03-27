import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.ObjectOutputStream;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;

public class RSAJavaKeyFileGenerator {
	/**
	 * 由于第三方慧能达支付公司使用的是java语言，密钥文件格式与python版本不同
	 * 所以为了使双方能够正常加密解密，使用该程序生成pem文件和key文件
	 * pem文件我们在python程序中使用，key文件交给慧能达使用
	 * @author duhao
	 */
	private static String privateKeyFile = "./pri3.key";
	private static String publicKeyFile = "./pub3.key";
	
	private static String privatePemFile = "./private3.pem";
	private static String publicPemFile = "./public3.pem";
	
	public static void main(String[] args) throws Exception {
		KeyPairGenerator keyPairGen = KeyPairGenerator.getInstance("RSA");
		// 初始化密钥对生成器，密钥大小为2048位  
		keyPairGen.initialize(2048);
		// 生成一个密钥对，保存在keyPair中
		KeyPair keyPair = keyPairGen.generateKeyPair();
		// 得到私钥
		RSAPrivateKey privateKey = (RSAPrivateKey) keyPair.getPrivate();
		// 得到公钥
		RSAPublicKey publicKey = (RSAPublicKey) keyPair.getPublic();
		
		// 生成python使用的pem文件
		String publicKeyString=Base64Utils.encode(publicKey.getEncoded());
		String privateKeyString=Base64Utils.encode(privateKey.getEncoded());
		FileWriter fw = new FileWriter(privatePemFile);
		fw.write("-----BEGIN PRIVATE KEY-----\n");
		fw.write(privateKeyString + "\n");
		fw.write("-----END PRIVATE KEY-----");
		fw.close();
		
		fw = new FileWriter(publicPemFile);
		fw.write("-----BEGIN PUBLIC KEY-----\n");
		fw.write(publicKeyString + "\n");
		fw.write("-----END PUBLIC KEY-----");
		fw.close();
		
		// 生成java使用的key文件
		ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(privateKeyFile));
		oos.writeObject(privateKey);
		oos.flush();
		oos.close();

		oos = new ObjectOutputStream(new FileOutputStream(publicKeyFile));
		oos.writeObject(publicKey);
		oos.flush();
		oos.close();
		
		System.out.println("generate key string and key file ok!");
	}
}
