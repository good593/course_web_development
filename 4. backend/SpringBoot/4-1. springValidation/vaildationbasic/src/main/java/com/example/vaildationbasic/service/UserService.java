package com.example.vaildationbasic.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.vaildationbasic.model.dao.UserDao;
import com.example.vaildationbasic.model.dto.UserDto;
import com.example.vaildationbasic.model.dto.UserValidDto;
import com.example.vaildationbasic.model.entity.UserEntity;

@Service
public class UserService {
    
    @Autowired
    private UserDao uDao;

    public void insertUser(UserDto dto) {
        UserEntity entity = new UserEntity();
        entity.setId(dto.getId());
        entity.setName(dto.getName());
        entity.setPassword(dto.getPassword());
        entity.setAge(dto.getAge());
        entity.setEmail(dto.getEmail());
        entity.setPhoneNumber(dto.getPhoneNumber());

        uDao.insertUser(entity);
    }

    public void insertUserWithValid(UserValidDto dto) {
        UserEntity entity = new UserEntity();
        entity.setId(dto.getId());
        entity.setName(dto.getName());
        entity.setPassword(dto.getPassword());
        entity.setAge(dto.getAge());
        entity.setEmail(dto.getEmail());
        entity.setPhoneNumber(dto.getPhoneNumber());

        uDao.insertUser(entity);
    }

    public UserDto getReferenceById(String id) {
        UserEntity entity = uDao.getReferenceById(id);
        UserDto dto = new UserDto();
        dto.setId(entity.getId());
        dto.setName(entity.getName());
        dto.setPassword(entity.getPassword());
        dto.setAge(entity.getAge());
        dto.setEmail(entity.getEmail());
        dto.setPhoneNumber(entity.getPhoneNumber());

        return dto;
    }

}
