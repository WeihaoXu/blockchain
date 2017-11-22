sample_block = {
    "timestamp": "09/16/1994", 
    "miner": "weihao",
    "transactions": "Na send Weihao 10 coins",
    "hash": "PsH8R72JQ3SOdhVi3uxftmaW6Vc51MKb0q5P2rRUpPvrszuE4W1povHYgTpBfshb",
    "prev_hash": "PsH8R72JQ3SOdhVi3uxftmaW6Vc51MKb0q5P2rRUpPvrszuE4W1povHYgTpBfshb"

}


var PORTS = [5000, 5001, 5002, 5003, 5004]
var template
var refreshIntervalVar




$(document).ready(function() {
    template = $('#block_template').html()
    registerButtons()
    startMining()

})

function update_all_views() {
    for(var i = 0; i < 5; i++) {
        update_view(i)
    }
}

function update_view(chainNumber) {
    console.log(chainNumber)
    var port = (5000 + chainNumber).toString()
    console.log("update port: " + port)
    updateChain(port, chainNumber)
    //renderData(chainNumber, blocks)
}

function updateChain(port, chainNumber) {
    var getChainUrl = "http://127.0.0.1:" + port + "/view"
    $.ajax({
        url: getChainUrl, 
        type: 'GET',
        crossDomain: true,
        dataType: 'json',
        success: function(data){
            var blocks = data['blocks']
            console.log(blocks)
            renderData(chainNumber, blocks)
        },
    });
}

function renderData(chainNumber, blocks) {
    var toRender = ""
    var chainID = "#chain" + chainNumber
    for(var i = 0; i < blocks.length; i++) {
        blockStr = renderBlock(blocks[i])
        toRender = toRender.concat(blockStr)
    }
    $(chainID).html(toRender)
}

function renderBlock(block_dict) {
    //Render the data into the template
    var block = Mustache.render(template, {
        index: block_dict["index"], 
        prev_hash: block_dict["prev_hash"], 
        hash: block_dict["hashcode"],
        transactions: block_dict["transactions"]
    })
    return block
}

function registerButtons() {
    $("#refresh-view").click(function(){
        update_all_views()
    })

    $("#auto-refresh").click(function(){
        $(this).toggleClass('active')
        if($(this).hasClass('active')) {
            refreshIntervalVar = setInterval(update_all_views, 1000)
        }
        else {
            clearInterval(refreshIntervalVar)
        }
    })

    $("#send-transaction").click(function() {
        var port = $("#port-sel").val()
        send_tx_url = "http://localhost:" + port + "/receive_transaction"
        transaction = {
            "sender": $("#tx-from").val(),
            "receiver": $("#tx-to").val(),
            "value": $("#tx-value").val(),
            "timestamp": new Date().toString()
        }

        $.ajax({
            url: send_tx_url, 
            type: 'POST',
            data: transaction,
            crossDomain: true,
            dataType: 'json',
            success: function(data){
                alert("transaction sent")
            }
        });
    })
}

function startMining() {
    for(var i = 0; i < PORTS.length; i++) {
        startPort(PORTS[i])
    }
}

function startPort(port) {
    mineURL = "http://localhost:" + port + "/mine"
    $.ajax({
        url: mineURL, 
        type: 'GET',
        crossDomain: true,
        dataType: 'json',
        success: function(data){
            alert("port " + port + "start mining")
        }
    });
}













