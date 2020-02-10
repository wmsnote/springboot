# JAVA日志MDC追踪快速定位问题源头


## 一、了解MDC

### MDC是什么

  MDC（Mapped Diagnostic Context，映射调试上下文）是 log4j 和 logback 提供的一种方便在多线程条件下记录日志的功能，也可以说是一种轻量级的日志跟踪工具。

### MDC能做什么

  那么通过MDC的概念，我们可以知道，MDC是应用内的线程级别，不是分布式的应用层级别，所以仅靠它无法做到分布式应用调用链路跟踪的需求。它要解决的问题主要是让我们可以在海量日志数据中快速捞到可用的日志信息。

### 场景分析

  既然我们知道MDC可以让我们快速的捞到可用的日志信息，那具体怎么捞呢？我们先来看这样的一个场景：很多时候，我们一个程序调用链可能会很复杂，并且在调用链的各个环节中，会对一些关键的操作做日志埋点，比如说入参出参、复杂计算后的结果等等信息，但在线上环境是很多用户使用我们功能的，比如说A程序，每个用户都在使用了A程序后，打印了A程序方法调用链内的所以日志，那我怎么就知道这一堆相同日志中，哪些是同一次请求所打印的呢？可能大家会说：可以看它的线程名啊，HTTP在同一请求中会用同一个线程。一定程度上看线程是可以的，但我们也知道，web服务器不可能无限创建线程的，它内部有个线程池，用于HTTP线程的创建、回收等管理，如果该程序使用频率是很高，那完全有可能短时间内的几次请求用的都是同一个线程，这样的话就解决不了上述所说的：“把一次请求中调用链内的所以日志找出来”的需求了。

### 解决方案 

  针对以上的场景，我们可以在一次请求进来的时候，创建一个全局唯一的标识符，该标识符可以没有业务含义，我们就叫它做“traceId”吧，因为这仅仅只是为了区分每次请求打印了什么信息，接下来，我们知道ThreadLocal这个类是可以共享线程内的数据的，所以我们就可以利用它来实现这个需求了。把traceId放入到ThreadLocal中，然后在我们程序调用链中输出日志时，就可以带上这个traceId了，比如以下代码：

```java
String traceId = threadLocal.get();
log.info("这里是打印信息{}", traceId);
```

  以上方法虽然解决了我们的问题，但是我们每次打印日志都要自己拿一下traceId，这无形增加了我们的工作量和降低了代码的美观度，所以我们肯定得想办法封装这部分重复的代码了。而这个封装的事情MDC就帮我们做了，我们只管在请求最开始时，生成一个traceId，然后放到MDC中就可以了，之后的事情就是按照我们原来的方式打印日志，不用新增其他额外的重复代码，这个traceId也一直跟随这个线程的执行完所有的任务。

## 二、具体实现

### 实现前效果

  我们先来看看实现MDC前的日志打印效果。我们以logback为例，在配置文件中，定义的日志格式为：
`<pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} %thread | [%X{X-B3-TraceId}] | %-5level %logger{50} %msg%n</pattern>`
代码我们打印的日志要包含以下信息：日志打印的时间、线程、TraceId、级别、哪个类打印的和具体打印信息吗，其中%X{X-B3-TraceId}就是我们接下来要讲的内容。跑一下应用看看当前的日志长啥样：

```log
#第一次请求
2019-08-10 15:34:36.428 http-nio-9191-exec-1 | [] | INFO  com.lhp.aspects.RequestLogAspect 请求IP：0:0:0:0:0:0:0:1
2019-08-10 15:34:36.428 http-nio-9191-exec-1 | [] | INFO  com.lhp.aspects.RequestLogAspect 请求路径：http://localhost:9191/mdcTest
2019-08-10 15:34:36.428 http-nio-9191-exec-1 | [] | INFO  com.lhp.aspects.RequestLogAspect 请求方式：GET
2019-08-10 15:34:36.430 http-nio-9191-exec-1 | [] | INFO  com.lhp.aspects.RequestLogAspect 方法描述：
2019-08-10 15:34:36.434 http-nio-9191-exec-1 | [] | INFO  com.lhp.aspects.RequestLogAspect 请求参数：{}
2019-08-10 15:34:36.438 http-nio-9191-exec-1 | [] | INFO  com.lhp.pmj.controller.BackDoorController invoke controller method=mdcControllerTest param=罗海鹏
2019-08-10 15:34:36.511 http-nio-9191-exec-1 | [] | INFO  c.s.p.o.l.facade.impl.XxxFacade invoke facade method=mdcFacadeTest param=罗海鹏trace
2019-08-10 15:34:36.631 http-nio-9191-exec-1 | [] | INFO  com.lhp.aspects.RequestLogAspect 请求出参: "MDC测试"
2019-08-10 15:34:36.631 http-nio-9191-exec-1 | [] | INFO  com.lhp.aspects.RequestLogAspect 执行时间: 203
 
#第二次请求
2019-08-10 15:39:40.966 http-nio-9191-exec-1 | [] | INFO  com.lhp.aspects.RequestLogAspect 请求IP：0:0:0:0:0:0:0:1
2019-08-10 15:39:40.966 http-nio-9191-exec-1 | [] | INFO  com.lhp.aspects.RequestLogAspect 请求路径：http://localhost:9191/mdcTest
2019-08-10 15:39:40.966 http-nio-9191-exec-1 | [] | INFO  com.lhp.aspects.RequestLogAspect 请求方式：GET
2019-08-10 15:39:41.025 http-nio-9191-exec-1 | [] | INFO  com.lhp.aspects.RequestLogAspect 方法描述：
2019-08-10 15:39:41.144 http-nio-9191-exec-1 | [] | INFO  com.lhp.aspects.RequestLogAspect 请求参数：{}
2019-08-10 15:39:41.145 http-nio-9191-exec-1 | [] | INFO  com.lhp.pmj.controller.BackDoorController invoke controller method=mdcControllerTest param=罗海鹏
2019-08-10 15:39:41.145 http-nio-9191-exec-1 | [] | INFO  c.s.p.o.l.facade.impl.XxxFacade invoke facade method=mdcFacadeTest param=罗海鹏trace
2019-08-10 15:39:41.855 http-nio-9191-exec-1 | [] | INFO  com.lhp.aspects.RequestLogAspect 请求出参: "MDC测试"
2019-08-10 15:39:41.857 http-nio-9191-exec-1 | [] | INFO  com.lhp.aspects.RequestLogAspect 执行时间: 203
```

通过上述打印的日志可以看出问题了，两次请求，刚好分配了同一个线程http-nio-9191-exec-1处理，这样我们在海量日志数据的情况下，就很难区分每次请求分别打印了哪一些日志了。

实现后效果

  在上面演示中，我们看到输出的日志中，有个“[ ]”的字符串，这一块信息是我们在定义日志格式中的“[%X{X-B3-TraceId}]”，%X{ }是取值的意思，告诉日志框架，需要去MDC获取key为X-B3-TraceId的值，很明显，我们并没有给MDC设置一个key为X-B3-TraceId的值，所以当我们打印日志的时候，这一块就打印成空字符串了。下面我们来看看给MDC设置了值之后的效果。

创建并设置traceId 

我们以SpringMVC为例，在请求最开始时创建traceId，并把该traceId放到MDC中：这一步我们可以使用SpringMVC的拦截器或者AOP来实现。而这里的例子我就使用AOP来实现。

1、定义切点

```java
    /**
     * controller的切点
     */
    @Pointcut("execution(public * com.lhp.*.controller..*.*(..))")
    public void controllerTraceId() {
    }

```

2、环绕切入

```java
    /**
     * 所有controller环绕切点
     *
     * @param proceedingJoinPoint 切入点
     * @return Object
     * @throws Throwable 异常
     */
    @Around("controllerTraceId()")
    public Object doControllerAround(ProceedingJoinPoint proceedingJoinPoint) throws Throwable {
        MDC.put("X-B3-TraceId", UUID.randomUUID().toString());
        Object result = proceedingJoinPoint.proceed();
        MDC.clear();
        return result;
    }

```

  需要操作MDC很简单，使用的工具类就叫做MDC，它是slf4j提供的日志标准包下的一个类，log4j和logback都有实现，然后往MDC设置一个key为X-B3-TraceId的值，X-B3-TraceId就是我们上述日志格式定义的%X{X-B3-TraceId}。value需要唯一，并且不需要有业务含义，所以我这里直接使用UUID。接着AOP的proceedingJoinPoint.proceed()执行完后，我们的方法也就执行完了，要调用MDC.clear()把报错到当前线程的MDC数据清空。

3、查看效果

```log
#第一次请求
2019-08-10 16:29:51.494 http-nio-9191-exec-2 | [807d770b-b44b-4cc3-80d0-91e47b0baf34] | INFO  com.lhp.aspects.RequestLogAspect 请求IP：0:0:0:0:0:0:0:1
2019-08-10 16:29:51.494 http-nio-9191-exec-2 | [807d770b-b44b-4cc3-80d0-91e47b0baf34] | INFO  com.lhp.aspects.RequestLogAspect 请求路径：http://localhost:9191/mdcTest
2019-08-10 16:29:51.494 http-nio-9191-exec-2 | [807d770b-b44b-4cc3-80d0-91e47b0baf34] | INFO  com.lhp.aspects.RequestLogAspect 请求方式：GET
2019-08-10 16:29:51.496 http-nio-9191-exec-2 | [807d770b-b44b-4cc3-80d0-91e47b0baf34] | INFO  com.lhp.aspects.RequestLogAspect 方法描述：
2019-08-10 16:29:51.498 http-nio-9191-exec-2 | [807d770b-b44b-4cc3-80d0-91e47b0baf34] | INFO  com.lhp.aspects.RequestLogAspect 请求参数：{}
2019-08-10 16:29:51.501 http-nio-9191-exec-2 | [807d770b-b44b-4cc3-80d0-91e47b0baf34] | INFO  com.lhp.controller.BackDoorController invoke controller method=mdcControllerTest param=罗海鹏
2019-08-10 16:29:51.560 http-nio-9191-exec-2 | [807d770b-b44b-4cc3-80d0-91e47b0baf34] | INFO  c.s.p.o.l.facade.impl.XxxFacade invoke facade method=mdcFacadeTest param=罗海鹏trace
2019-08-10 16:29:51.677 http-nio-9191-exec-2 | [807d770b-b44b-4cc3-80d0-91e47b0baf34] | INFO  com.lhp.aspects.RequestLogAspect 请求出参: "MDC测试"
2019-08-10 16:29:51.677 http-nio-9191-exec-2 | [807d770b-b44b-4cc3-80d0-91e47b0baf34] | INFO  com.lhp.aspects.RequestLogAspect 执行时间: 183
 
#第二次请求
2019-08-10 16:34:04.709 http-nio-9191-exec-2 | [59123bc7-a03e-41b6-89fc-cf984369896c] | INFO  com.lhp.aspects.RequestLogAspect 请求IP：0:0:0:0:0:0:0:1
2019-08-10 16:34:04.709 http-nio-9191-exec-2 | [59123bc7-a03e-41b6-89fc-cf984369896c] | INFO  com.lhp.aspects.RequestLogAspect 请求路径：http://localhost:9191/mdcTest
2019-08-10 16:34:04.709 http-nio-9191-exec-2 | [59123bc7-a03e-41b6-89fc-cf984369896c] | INFO  com.lhp.aspects.RequestLogAspect 请求方式：GET
2019-08-10 16:34:04.709 http-nio-9191-exec-2 | [59123bc7-a03e-41b6-89fc-cf984369896c] | INFO  com.lhp.aspects.RequestLogAspect 方法描述：
2019-08-10 16:34:04.709 http-nio-9191-exec-2 | [59123bc7-a03e-41b6-89fc-cf984369896c] | INFO  com.lhp.aspects.RequestLogAspect 请求参数：{}
2019-08-10 16:34:04.709 http-nio-9191-exec-2 | [59123bc7-a03e-41b6-89fc-cf984369896c] | INFO  com.lhp.controller.BackDoorController invoke controller method=mdcControllerTest param=罗海鹏
2019-08-10 16:34:04.766 http-nio-9191-exec-2 | [59123bc7-a03e-41b6-89fc-cf984369896c] | INFO  c.s.p.o.l.facade.impl.XxxFacade invoke facade method=mdcFacadeTest param=罗海鹏trace
2019-08-10 16:34:04.883 http-nio-9191-exec-2 | [59123bc7-a03e-41b6-89fc-cf984369896c] | INFO  com.lhp.aspects.RequestLogAspect 请求出参: "MDC测试"
2019-08-10 16:34:04.883 http-nio-9191-exec-2 | [59123bc7-a03e-41b6-89fc-cf984369896c] | INFO  com.lhp.aspects.RequestLogAspect 执行时间: 174
``` 


可以看到，这次日志输出%X{X-B3-TraceId}的位置就不在是空了，而是一串UUID，并且在一次请求之内，UUID都是一样的，这样我们在排查问题时，首先找到了问题的入口日志，在搜索该日志的UUID，就整个请求内的所有日志找出来了，提高了我们排查问题的效率。

##　三、MDC原理

通过以上的实现，我们发现MDC使用起来非常简单，就只有两个步骤：

1、定义日志格式，其中%X{}代表去MDC取值
2、通过拦截器或者AOP在方法调用链最开始，设置MDC的值
接下来我们看看它的实现：

![](https://imgconvert.csdnimg.cn/aHR0cHM6Ly91cGxvYWQtaW1hZ2VzLmppYW5zaHUuaW8vdXBsb2FkX2ltYWdlcy8xMDU3NDkyMi1mNjc1MjRhMmQ3NTQ4YzIxLnBuZw?x-oss-process=image/format,png)

## 四、子线程MDC传递

  既然我们知道MDC底层使用TreadLocal来实现，那根据TreadLocal的特点，它是可以让我们在同一个线程中共享数据的，但是往往我们在业务方法中，会开启多线程来执行程序，这样的话MDC就无法传递到其他子线程了。这时，我们需要使用额外的方法来传递存在TreadLocal里的值。MDC提供了一个叫getCopyOfContextMap的方法，很显然，该方法就是把当前线程TreadLocal绑定的Map获取出来，之后就是把该Map绑定到子线程中的ThreadLocal中了，具体代码如下：

```java
        Map<String, String> copyOfContextMap = MDC.getCopyOfContextMap();
        new Thread(() -> {
            if (copyOfContextMap != null) {
                MDC.setContextMap(copyOfContextMap);
            }
            log.info("这个是子线程的信息");
        }).start();

```

也就是说，我们在主线程中获取MDC的值，然后在子线程中设置进去，这样，子线程打印的信息也会带有整个调用链共同的traceId了。

