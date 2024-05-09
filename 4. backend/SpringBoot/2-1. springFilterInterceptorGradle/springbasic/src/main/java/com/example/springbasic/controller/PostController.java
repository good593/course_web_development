package com.example.springbasic.controller;

import java.util.HashMap;
import java.util.Map;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.springbasic.model.UserDto;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@RestController
@RequestMapping("/api/v1/post")
public class PostController {

    // localhost:8080/api/v1/post/header
    @PostMapping("/header")
    public Map<String, Object> getHeader(
        @RequestHeader("Referer") String referer, @RequestHeader("User-Agent") String user_agent) {

        Map<String, Object> map = new HashMap<>();
        map.put("Referer", referer);
        map.put("User-Agent", user_agent);
        return map;
    }
    
    // localhost:8080/api/v1/post/variable1
    @PostMapping("/variable1")
    public String postVariable1(@RequestBody Map<String, Object> params) {
        log.info("[PostController][postVariable1] Start");
        params.forEach((strKey, strValue)->{
            // System.out.println( strKey +":"+ strValue );
            log.info("[postVariable1] "+strKey +":"+ strValue);
        });
        return "postVariable1";
    }

    // localhost:8080/api/v1/post/variable2
    @PostMapping("/variable2")
    public String postVariable2(@RequestBody UserDto dto) {
        log.info("[PostController][postVariable2] Start");

        log.info(dto.toString());
        return "postVariable2";
    }

}
