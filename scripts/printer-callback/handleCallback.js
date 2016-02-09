var express = require('express');
var bodyParser = require('body-parser');

var app = express();

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());


app.get('/', function (req, res) {
    res.send('Hello!');
});

app.post('/handlePrinterStatusUpdate', function (req, res) {
    console.log("\nSomebody is calling POST handlePrinterStatusUpdate ! ", req.body );
    return res.status(200).json({ "response" : "Hello! Update status has been handled" });
});

app.get('/handlePrinterStatusUpdate', function (req, res) {
    console.log("Somebody is calling GET handlePrinterStatusUpdate ! " );
    return res.status(200).json({ "response" : "Hello! Update status has been handled" });
});

app.get('/handlePrinterStatusUpdate/support', function (req, res) {
    console.log("Somebody is testing if the callback is supported.");
    return res.status(200).json({ "callback" : "supported" });
});

var server = app.listen(3001, function () {
    var port = server.address().port;
    console.log('Running on port: %s', port);
});