package com.example.springbasic.controller;

import java.util.HashMap;
import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.example.springbasic.model.UserDto;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@RestController
@RequestMapping("/api/v1/get")
public class GetContoller {
    
    // localhost:8080/api/v1/get/hello
    @GetMapping("/hello")
    public String getHello() {
        return "Hello World";
    }

    // localhost:8080/api/v1/get/header
    @GetMapping("/header")
    public Map<String, Object> getHeader(
        @RequestHeader("Referer") String referer, @RequestHeader("User-Agent") String user_agent) {

        Map<String, Object> map = new HashMap<>();
        map.put("Referer", referer);
        map.put("User-Agent", user_agent);
        return map;
    }

    // localhost:8080/api/v1/get/variable1/hi
    @GetMapping("/variable1/{param}")
    public String getVariable1(@PathVariable String param) {
        return param;
    }

    // localhost:8080/api/v1/get/variable2/hi
    @GetMapping("/variable2/{param}")
    public String getVariable2(@PathVariable("param") String variable) {
        return variable;
    }

    // localhost:8080/api/v1/get/variable3/hello/world
    @GetMapping("/variable3/{param1}/{param2}")
    public String getVariable3(@PathVariable String param1, @PathVariable String param2) {
        return param1 + " / "+ param2;
    }

    // localhost:8080/api/v1/get/query1?name=hi
    @GetMapping("/query1")
    public String getQuery1(@RequestParam String name) {
        return name;
    }

    // localhost:8080/api/v1/get/query2?name=name1&email=sample@gmail.com
    @GetMapping("/query2")
    public String getQuery2(@RequestParam String name, @RequestParam String email) {
        return name + " / " + email;
    }

    // localhost:8080/api/v1/get/query3/hello/world?name=name1&email=sample@gmail.com
    @GetMapping("/query3/{param1}/{param2}")
    public String getQuery3(
        @PathVariable String param1, @PathVariable String param2
        , @RequestParam String name, @RequestParam String email) {
        return param1 + " / "+ param2 +" / "+ name + " / " + email;
    }

    // localhost:8080/api/v1/get/query4?name=name1&email=sample@gmail.com&age=33
    @GetMapping("/query4")
    public String getQuery4(@RequestParam Map<String, Object> params) {
        log.info("[GetContoller][getQuery4] Start");
        params.forEach((strKey, strValue)->{
            // System.out.println( strKey +":"+ strValue );
            log.info("[getQuery4] "+strKey +":"+ strValue);
        });
        return "getQeury4";
    }

    // localhost:8080/api/v1/get/query5?name=name1&email=sample@gmail.com&age=33
    @GetMapping("/query5")
    public String getQuery5(@ModelAttribute UserDto dto) {
        log.info("[GetContoller][query5] Start");

        log.info("name: "+dto.getName());
        log.info("email: "+dto.getEmail());
        log.info("age: "+dto.getAge());
        return "getQeury5: "+dto.toString();
    }

}
