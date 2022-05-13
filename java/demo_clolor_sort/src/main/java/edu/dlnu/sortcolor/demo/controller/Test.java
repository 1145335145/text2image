package edu.dlnu.sortcolor.demo.controller;

import edu.dlnu.sortcolor.demo.service.QueueService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;

@RestController
public class Test {
    @Autowired
    private QueueService queueService;
    @PostMapping("/getImage")
    public List<String> sendImageToProcessQueue(@RequestBody Map<String, String> param){
        List<String> result = null;
        Future<List<String>> future;
        try {
            future = queueService.SendImageToProcessQueue(param);
            result = future.get();
        } catch (InterruptedException | ExecutionException e) {
            e.printStackTrace();
        }
        return result;
    }
}
