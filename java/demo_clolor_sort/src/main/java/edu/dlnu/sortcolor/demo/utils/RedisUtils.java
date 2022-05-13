package edu.dlnu.sortcolor.demo.utils;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;

import java.util.HashMap;
import java.util.List;

@Component

public class RedisUtils {
    @Autowired
    private  JedisPool redisPollFactory;
    private Logger log = LoggerFactory.getLogger(this.getClass());

    private final int EXPIRE = 60*60*24*30;

    public List<String> getResult(String taskId){
        List<String> strings = null;
        try (Jedis jedis = redisPollFactory.getResource()){
//          strings =  jedis.hmget("resultHashPool",taskId+"1",taskId+"2",taskId+"3",
//                    taskId+"4",taskId+"5");
            strings = jedis.lrange("result_list_"+taskId,0,19);
        }catch (Exception e){
            log.error(e.toString());
        }
        return strings;


    }

    public void addTaskToQueue(String taskId){
        try (Jedis jedis = redisPollFactory.getResource()){
            jedis.lpush("taskQueue", taskId);
        }catch (Exception e){
            log.error(e.toString());
        }
    }
    public void addTaskToHash(String taskId,String textInfo){
        HashMap<String,String> infoMap  = new HashMap<>();
        infoMap.put(taskId,textInfo);

        try (Jedis jedis = redisPollFactory.getResource()){
            jedis.hmset("processHashPoll",infoMap);

        }catch (Exception e){
            log.error(e.toString()+"add task to hash");
        }
    }

    public String set(String key,String value){
        Jedis jedis = redisPollFactory.getResource();
        return jedis.set(key, value);
    }

    public String get(String key){
        Jedis jedis = redisPollFactory.getResource();
        return jedis.get(key);

    }

    public String getToken(String id){
        String token = null;
        try (Jedis jedis = redisPollFactory.getResource()){
            token = jedis.get(id);
        }catch (Exception e){
            log.error(e.toString());
        }
        return token;
    }

    public  String addToken(String token,String id){
        String set = null;
        try (Jedis jedis = redisPollFactory.getResource()) {
             set = jedis.set(id, token);
        } catch (Exception e) {
            log.error(e.toString());
        }
        return set;
    }
    public Long delToken(String... tokenKeys){
        Long res = null;
        try(Jedis jedis = redisPollFactory.getResource()){
            res = jedis.del(tokenKeys);
        }catch (Exception e){
            log.info(e.toString());
        }
        return res;
    }

}
