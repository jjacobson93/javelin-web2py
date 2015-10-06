function range(start, end, step) {
    var range = [];
    var typeofStart = typeof start;
    var typeofEnd = typeof end;

    if (step === 0) {
        throw TypeError("Step cannot be zero.");
    }

    if (typeofStart == "undefined" || typeofEnd == "undefined") {
        throw TypeError("Must pass start and end arguments.");
    } else if (typeofStart != typeofEnd) {
        throw TypeError("Start and end arguments must be of same type.");
    }

    typeof step == "undefined" && (step = 1);

    if (end < start) {
        step = -step;
    }

    if (typeofStart == "number") {

        while (step > 0 ? end >= start : end <= start) {
            range.push(start);
            start += step;
        }

    } else if (typeofStart == "string") {

        if (start.length != 1 || end.length != 1) {
            throw TypeError("Only strings with one character are supported.");
        }

        start = start.charCodeAt(0);
        end = end.charCodeAt(0);

        while (step > 0 ? end >= start : end <= start) {
            range.push(String.fromCharCode(start));
            start += step;
        }

    } else {
        throw TypeError("Only string and number types are supported");
    }

    return range;
}

function notify(status, text) {
    if (status == "error") {
        $('.notification').css('background-color', '#E74C3C');
    } else if (status == "warn") {
        $('.notification').css('background-color', '#F1C40F');
    } else if (status == "success") {
        $('.notification').css('background-color', '#2ECC71');
    } else {
        $('.notification').css('background-color', '#3498DB');
    }

    $('.notification .overlay p').html('<i class="fa fa-exclamation-triangle"></i> ' + text);
    $('.notification').animate({right: "20px"}, 500);
    setTimeout(function() {
        $('.notification').animate({right: "-30%"}, 500);
    }, 4000);
}

function getPeople($http) {
    return $http.get('/api/people');
}