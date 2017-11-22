sample_block = {
    "timestamp": "09/16/1994", 
    "miner": "weihao",
    "transactions": "Na send Weihao 10 coins",
    "hash": "PsH8R72JQ3SOdhVi3uxftmaW6Vc51MKb0q5P2rRUpPvrszuE4W1povHYgTpBfshb",
    "prev_hash": "PsH8R72JQ3SOdhVi3uxftmaW6Vc51MKb0q5P2rRUpPvrszuE4W1povHYgTpBfshb"

}


var PORTS = [5000, 5001, 5002, 5003, 5004]
var template;




$(document).ready(function() {
    template = $('#block_template').html()
    setInterval(update_all_views, 1000)

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
    var getChainUrl = "http://127.0.0.1:" + port + "/chain"
    $.ajax({
        url: getChainUrl, 
        type: 'GET',
        crossDomain: true,
        dataType: 'json',
        success: function(data){
            var blocks = data['chain']['blocks']
            console.log("get data successful")
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
        prev_hash: block_dict["prev_hash"], 
        hash: block_dict["hashcode"],
        miner: "weihao" 
    })
    return block
}



