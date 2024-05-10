package com.example.basic.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.example.basic.model.UserDto;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@RestController
@RequestMapping("/api/v1/user")
public class UserController {
    
    // localhost:8080/api/v1/user/hello
    @GetMapping("/hello")
    public String getHello() throws Exception {

        log.info("[UserController][getHello] Start");
        Thread.sleep(1000); //1초 대기
        return "Hello World from UserController";
    }

    // localhost:8080/api/v1/user/query1?name=name1&email=sample@gmail.com
    @GetMapping("/query1")
    public String getQuery1(@RequestParam String name, @RequestParam String email) {

        log.info("[UserController][getQuery1] Start");
        return name + " / " + email;
    }

    // localhost:8080/api/v1/user/query2/hello/world?name=name1&email=sample@gmail.com
    @GetMapping("/query2/{param1}/{param2}")
    public String getQuery2(
        @PathVariable String param1, @PathVariable String param2
        , @RequestParam String name, @RequestParam String email) {

        log.info("[UserController][getQuery2] Start");
        return param1 + " / "+ param2 +" / "+ name + " / " + email;
    }

    // localhost:8080/api/v1/user/query3?name=name1&email=sample@gmail.com&age=33
    @GetMapping("/query3")
    public String getQuery3(@ModelAttribute UserDto dto) {

        log.info("[UserController][getQuery3] Start");
        return "getQeury3: "+dto.toString();
    }

    // localhost:8080/api/v1/user/post
    @PostMapping("/post")
    public String postDto(@RequestBody UserDto dto) {

        log.info("[UserController][postDto] Start");
        return "post: "+dto.toString();
    }
}
