package com.example.vaildationbasic.model.dao;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.vaildationbasic.model.entity.UserEntity;
import com.example.vaildationbasic.model.repository.UserRepository;

@Service
public class UserDao {

    @Autowired
    private UserRepository uRepository;

    public void insertUser(UserEntity entity) {
        uRepository.save(entity);
    }

    public UserEntity getReferenceById(String id) {
        return uRepository.getReferenceById(id);
    }
}
