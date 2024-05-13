package com.example.vaildationbasic.model.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@ToString
public class UserDto {
    private String id;
    private String name;
    private String password;
    private int age;
    private String email;
    private String phoneNumber;
}
