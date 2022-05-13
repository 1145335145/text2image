package edu.dlnu.sortcolor.demo.service;

import org.springframework.web.bind.annotation.RequestBody;

import java.util.List;
import java.util.Map;
import java.util.concurrent.Future;

public interface QueueService {
         Future<List<String>> SendImageToProcessQueue(@RequestBody Map<String, String> param) throws InterruptedException;
}
