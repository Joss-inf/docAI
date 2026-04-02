"""Tests for language parsers."""

from pathlib import Path

from codedocai.parser.base_parser import get_parser
from codedocai.semantic.ir_schema import Language


def test_python_parser(tmp_path: Path):
    source = """
import os
from typing import List

class MyController:
    '''Controller docstring.'''
    def __init__(self, name: str):
        self.name = name

    def execute(self, data: List[int]) -> bool:
        print("Executing")
        return True

async def fetch_data(url: str):
    return {}
"""
    file_path = tmp_path / "test.py"
    file_path.write_text(source)

    parser = get_parser("python")
    ir = parser.parse(file_path, "test.py")

    assert ir.language == Language.PYTHON
    assert len(ir.imports) == 2
    assert ir.imports[0].module == "os"
    assert ir.imports[1].module == "typing"
    assert ir.imports[1].names == ["List"]

    assert len(ir.classes) == 1
    cls = ir.classes[0]
    assert cls.name == "MyController"
    assert cls.docstring == "Controller docstring."
    assert len(cls.methods) == 2
    assert cls.methods[1].name == "execute"
    assert cls.methods[1].return_type == "bool"

    assert len(ir.functions) == 1
    func = ir.functions[0]
    assert func.name == "fetch_data"
    assert func.is_async is True
    assert func.params[0].name == "url"
    assert func.params[0].type_hint == "str"


def test_javascript_parser(tmp_path: Path):
    source = """
import {useState, useEffect} from 'react';
import axios from 'axios';

class ApiService {
    fetchUsers(limit) {
        return axios.get('/users');
    }
}

export const processData = (data) => {
    console.log(data);
}
"""
    file_path = tmp_path / "test.js"
    file_path.write_text(source)

    parser = get_parser("javascript")
    ir = parser.parse(file_path, "test.js")

    assert ir.language == Language.JAVASCRIPT
    assert len(ir.imports) == 2
    assert ir.imports[0].module == "react"
    assert ir.imports[0].names == ["useState", "useEffect"]

    assert len(ir.classes) == 1
    assert ir.classes[0].name == "ApiService"
    
    assert len(ir.functions) == 1
    assert ir.functions[0].name == "processData"


def test_rust_parser(tmp_path: Path):
    source = """
use std::collections::HashMap;
mod utils;

pub struct ServerConfig {
    port: u16,
}

impl ServerConfig {
    pub fn new(port: u16) -> Self {
        ServerConfig { port }
    }
}

async fn handle_request(req: Request) -> Result<(), Error> {
    Ok(())
}
"""
    file_path = tmp_path / "test.rs"
    file_path.write_text(source)

    parser = get_parser("rust")
    ir = parser.parse(file_path, "test.rs")

    assert ir.language == Language.RUST
    assert len(ir.imports) == 2
    assert ir.imports[0].module == "std::collections::HashMap"
    assert ir.imports[1].module == "utils"

    assert len(ir.classes) == 1
    cls = ir.classes[0]
    assert cls.name == "ServerConfig"
    assert len(cls.methods) == 1
    assert cls.methods[0].name == "new"
    assert cls.methods[0].params[0].name == "port"

    assert len(ir.functions) == 1
    func = ir.functions[0]
    assert func.name == "handle_request"
    assert func.is_async is True
    assert func.return_type == "Result<(), Error>"
