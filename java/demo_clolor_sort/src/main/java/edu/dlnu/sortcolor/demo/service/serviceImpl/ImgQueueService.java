package edu.dlnu.sortcolor.demo.service.serviceImpl;
import edu.dlnu.sortcolor.demo.service.QueueService;
import edu.dlnu.sortcolor.demo.utils.RedisUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.AsyncResult;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Future;

@Service
public class ImgQueueService implements QueueService {
    @Autowired
    private RedisUtils redisUtils;
    @Override
    @Async("asyncServiceExecutor")
    public Future<List<String>> SendImageToProcessQueue(Map<String, String> param)  {

        /*
          1.前端发来任务（taskId，img），后台收到后向 redis 的 “待处理任务队列” 发送一个任务号。
          2.后台向 redis 的 “待处理任务池hash” 加入任务。任务号为key，图像的base64的value。
          3.AI程序负责监听 “待处理任务队列” 若有新任务则处理任务，将该任务出队。
          4.AI程序得到结果，之后将任务结果加入 “已完成任务池hash”。任务号为key，图像的base64的value。
          5.后台轮询访问 “已完成任务池hash” 寻找对应已完成任务，找到任务之后将结果返回前端。
         */

        String taskId = param.get("taskId");
        String textInfo = param.get("textInfo");

        redisUtils.addTaskToHash(taskId,textInfo);
        redisUtils.addTaskToQueue(taskId);
        List<String> result = redisUtils.getResult(taskId);
        int cnt = 0;
        while (result.size()<20){
            result = redisUtils.getResult(taskId);
            cnt++;
            if (cnt>=2500){
                break;
            }
            try {
                Thread.sleep(5);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        return  new AsyncResult<>(result);
    }
}
