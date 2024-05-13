package com.example.basic.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.basic.model.BasicDto;
import com.example.basic.model.BasicLombokDto;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@RestController
@RequestMapping("/api/v1/get")
public class GetController {

    // http://localhost:8080/api/v1/get/basic/dto?name=name1&email=sample@gmail.com
    @GetMapping(value = "basic/dto")
    public String getBasicDto(@ModelAttribute BasicDto dto) {
        log.info("[GetController][getBasicDto] Start");
        return "GetMapping >> "+dto.toString();
    }

    // http://localhost:8080/api/v1/get/basiclombok/dto?name=name1&email=sample@gmail.com
    @GetMapping(value = "basiclombok/dto")
    public String getBasicLombokDto(@ModelAttribute BasicLombokDto dto) {
        log.info("[GetController][getBasicLombokDto] Start");
        return "GetMapping >> "+dto.toString();
    }

}
