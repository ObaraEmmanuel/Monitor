$.dajax = function (method, discovery_url, params, data, success, dataType) {
    return $.get(discovery_url, params).then(function (result) {
        return $[method](result['url'], data, success, dataType);
    });
};
