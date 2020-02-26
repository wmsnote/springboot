# 如何解决 lib 和 class 文件分离



```xml

<build>
		<plugins>
			<!--设置应用 Main 参数启动依赖查找的地址指向外部 lib 文件夹 -->
			<plugin>
				<groupId>org.apache.maven.plugins</groupId>
				<artifactId>maven-jar-plugin</artifactId>
				<configuration>
					<archive>
						<manifest>
							<addClasspath>true</addClasspath>
							<classpathPrefix>lib/</classpathPrefix>
						</manifest>
					</archive>
				</configuration>
			</plugin>
			<!--设置 SpringBoot 打包插件不包含任何 Jar 依赖包 -->
			<plugin>
				<groupId>org.springframework.boot</groupId>
				<artifactId>spring-boot-maven-plugin</artifactId>
				<configuration>
					<includes>
						<include>
							<groupId>nothing</groupId>
							<artifactId>nothing</artifactId>
						</include>
					</includes>
				</configuration>
			</plugin>
			<!--设置将 lib 拷贝到应用 Jar 外面 -->
			<plugin>
				<groupId>org.apache.maven.plugins</groupId>
				<artifactId>maven-dependency-plugin</artifactId>
				<executions>
					<execution>
						<id>copy-dependencies</id>
						<phase>prepare-package</phase>
						<goals><goal>copy-dependencies</goal></goals>
						<configuration>
							<outputDirectory>${project.build.directory}/lib</outputDirectory>
						</configuration>
					</execution>
				</executions>
			</plugin>
		</plugins>
	</build>


```



```dockerfile

VOLUMEFROM openjdk:8u212-b04-jre-slim
VOLUME /tmp
COPY target/lib/ ./lib/
ADD target/*.jar app.jar
RUN sh -c 'touch/app.jar'
ENV JAVA_OPTS="-Duser.timezone=Asia/Shanghai"
ENV APP_OPTS=""
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -Djava.security.egd=file:/dev/./urandom -jar /app.jar $APP_OPTS"]



```























