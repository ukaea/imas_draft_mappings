#ifndef INJA_TEST_HPP
#define INJA_TEST_HPP

#include "inja/inja.hpp"

float test_cython() {
    return 42.5;
}

std::string test_render(std::string key) {
    inja::json data;
    data["indices"] = {1, 2, 3};
    return inja::render(key, data);
};

std::string test_render_wglobals(std::string temp_globals, std::string key) {
    inja::json data;
    data = inja::json::parse(temp_globals);
    data["indices"] = {1, 2, 3};
    
    return inja::render(key, data);
};

#endif
