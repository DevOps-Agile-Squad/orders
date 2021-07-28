$(() => {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    const updateOrderFormData = (res, method) => {
        if (method !== "search") {
            $("#order_id").val(res.id);
            $("#customer_id").val(res.customer_id);
            $("#address").val(res.address);
            $("#status").val(res.status); 
        } else {
            $("#order_id").val(res[0].id);
            $("#customer_id").val(res[0].customer_id);
            $("#address").val(res[0].address);
            $("#status").val(res[0].status);
        }
        
    }

    // Clears all form fields in Order form
    const clearOrderFormData = () => {
        $("#order_id").val("");
        $("#customer_id").val("");
        $("#address").val("");
        $("#status").val("Received");
    }

    // Updates the flash message area
    const flashMessage = (message) => {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // Clear search results for orders
    const clearOrderResults = () => {
        $("#search_results").empty(); 
        $("#search_results").append('<table class="table-striped" cellpadding="10">');
        let header = '<tr>'; 
        header += '<th style="width:10%">Order ID</th>'; 
        header += '<th style="width:20%">Customer ID</th>'; 
        header += '<th style="width:25%">Address</th>'; 
        header += '<th style="width:35%">Items</th>'; 
        header += '<th style="width:10%">Status</th>'; 
        $("#search_results").append(header);
    }
    
    // List the orders received from a request
    const listOrders = (res, method) => {
        clearOrderResults(); 
        if (method === "list" || method === "search") {
            for (let i = 0; i < res.length; i++) {
                const order = res[i]; 
                let itemsString = ""; 
                order.items.map((item) => {itemsString+=`${item.item_id}: ${item.item_name}; `})
                const row = "<tr><td>"+order.id+"</td><td>"+order.customer_id+"</td><td>"+order.address+"</td><td>"+itemsString+"</td><td>"+order.status+"</td></tr>";
                $("#search_results").append(row); 
            }
        } else {
            let itemsString = ""; 
            res.items.map((item) => {itemsString+=`${item.item_id}: ${item.item_name}; `})
            const row = "<tr><td>"+res.id+"</td><td>"+res.customer_id+"</td><td>"+res.address+"</td><td>"+itemsString+"</td><td>"+res.status+"</td></tr>";
            $("#search_results").append(row); 
        }
    }

    // Updates the Item form with data from the response
    const updateItemFormData = (res) => {
        $("#item_id").val(res.item_id);
        $("#item_order_id").val(res.order_id);
        $("#name").val(res.item_name);
        $("#quantity").val(res.quantity);
        $("#price").val(res.price); 
    }

    // Clears all form fields in Item form
    const clearItemFormData = () => {
        $("#item_id").val("");
        $("#item_order_id").val("");
        $("#name").val("");
        $("#quantity").val("");
        $("#price").val(""); 
    }

    // Clear search results for orders
    const clearItemResults = () => {
        $("#item_search_results").empty(); 
        $("#item_search_results").append('<table class="table-striped" cellpadding="10">');
        let header = '<tr>'; 
        header += '<th style="width:15%">Item ID</th>'; 
        header += '<th style="width:25%">Order ID</th>'; 
        header += '<th style="width:40%">Name</th>'; 
        header += '<th style="width:20%">Quantity</th>'; 
        header += '<th style="width:10%">Price</th>'; 
        $("#item_search_results").append(header);
    }

    // List the item(s) received from a request
    const listItem = (res) => {
        clearItemResults();
        const row = "<tr><td>"+res.item_id+"</td><td>"+res.order_id+"</td><td>"+res.item_name+"</td><td>"+res.quantity+"</td><td>"+res.price+"</td></tr>";
        $("#item_search_results").append(row); 
    }

    // ****************************************      
    // Create an Order
    // ****************************************

    $("#create-btn").click(() => {

        const customerId = $("#customer_id").val();
        const address = $("#address").val();
        const status = $("#status").val();

        const data = {
            "customer_id": parseInt(customerId),
            "address": address,
            "status": status,
            "items": []
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/orders",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done((res) => {
            updateOrderFormData(res, "create")
            flashMessage("Success")
        });

        ajax.fail(function(res){
            flashMessage(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update an Order
    // ****************************************

    $("#update-btn").click(() => {

        let orderId = $("#order_id").val();
        let customerId = $("#customer_id").val();
        let address = $("#address").val();
        const status = $("#status").val();

        const ajax = $.ajax({
            type: "GET",
            url: "/orders/" + orderId,
            contentType: "application/json",
            data: ''
        })

        ajax.done((res) => {
            customerId = customerId === "" ? res.customer_id : customerId; 
            address = address === "" ? res.address : address; 
            items = res.items; 
            console.log("items are: ", items)
            console.log("response is: ", res); 
            const data = {
                "customer_id": parseInt(customerId),
                "address": address,
                "status": status,
                // "item": items
            };

            const _ajax = $.ajax({
                type: "PUT",
                url: "/orders/" + orderId,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

            _ajax.done((res) => {
                updateOrderFormData(res, "update")
                listOrders(res, "update")
                flashMessage("Success")
            });

            _ajax.fail((res) => {
                flashMessage(res.responseJSON.message)
            });
            
        })

        ajax.fail((res) => {
            flashMessage(res.responseJSON.message)
        });
    });

    // ****************************************
    // Retrieve an Order
    // ****************************************

    $("#retrieve-btn").click(() => {

        const orderId = $("#order_id").val();

        const ajax = $.ajax({
            type: "GET",
            url: "/orders/" + orderId,
            contentType: "application/json",
            data: ''
        })
        

        ajax.done((res) => {
            console.log(res)
            //alert(res.toSource())
            listOrders(res, "retrieve")
            updateOrderFormData(res, "retrieve")
            flashMessage("Success")
        });

        ajax.fail((res) => {
            clearOrderFormData()
            flashMessage(res.responseJSON.message)
        });

    });

    // ****************************************
    // Search an Order by Customer ID
    // ****************************************

    $("#search-btn").click(() => {

        const customerId = $("#customer_id").val();

        const ajax = $.ajax({
            type: "GET",
            url: `/orders?customer_id=${customerId}`,
            contentType: "application/json",
            data: ''
        })
        

        ajax.done((res) => {
            if (res.length === 0){
                flashMessage("No orders found")
            }
            else {
                listOrders(res, "search")
                updateOrderFormData(res, "search")
                flashMessage("Success")
            }
        });

        ajax.fail((res) => {
            clearOrderFormData()
            flashMessage(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Order
    // ****************************************

    $("#delete-btn").click(() => {

        const orderId = $("#order_id").val();

        const ajax = $.ajax({
            type: "DELETE",
            url: "/orders/" + orderId,
            contentType: "application/json",
            data: '',
        })

        ajax.done((res) => {
            clearOrderFormData()
            clearOrderResults()
            flashMessage("Order has been Deleted!")
        });

        ajax.fail((res) => {
            flashMessage("Server error!")
        });
    });

    // ****************************************
    // Cancel an order
    // ****************************************
    $("#cancel-btn").click(() => {
        console.log("Cancelling order")
        const orderId = $("#order_id").val();
        const ajax = $.ajax({
            type: "POST",
            url: "/orders/" + orderId + "/cancel",
            contentType: "application/json",
            data: '',
        });

        ajax.done((res) => {
            clearOrderFormData()
            clearOrderResults()
            flashMessage("Order has been Cancelled!")
        });

        ajax.fail((res) => {
            flashMessage("Server error!")
        });

    })

    // ****************************************
    // Clear the Order form
    // ****************************************

    $("#clear-btn").click(() => {
        clearOrderFormData()
    });

    // ****************************************
    // List all orders
    // ****************************************
    $("#list-btn").click(() => {
        const ajax = $.ajax({
            type: "GET",
            url: "/orders",
            contentType: "application/json",
            data: ""
        }); 

        ajax.done((res) => {
            listOrders(res, "list"); 
            flashMessage("Success")
        }); 
    })

    // ****************************************
    // Clear the Item form
    // ****************************************

    $("#item-clear-btn").click(() => {
        clearItemFormData(); 
    });


    // ****************************************
    // Retrieve an Item
    // ****************************************

    $("#item-retrieve-btn").click(() => {

        const itemId = $("#item_id").val();
        const orderId = $("#item_order_id").val(); 

        if (!(itemId && orderId)) {
            alert("Please enter an Item ID and an Order ID."); 
            return; 
        }

        const ajax = $.ajax({
            type: "GET",
            url: `/orders/${orderId}/items/${itemId}`,
            contentType: "application/json",
            data: ''
        })
        

        ajax.done((res) => {
            listItem(res, "retrieve")
            updateItemFormData(res)
            flashMessage("Success")
        });

        ajax.fail(function(res){
            clearItemFormData()
            flashMessage(res.responseJSON.message)
        });

    });

    // ****************************************      
    // Create an Order
    // ****************************************

    $("#item-create-btn").click(() => {

        const orderId = $("#item_order_id").val();
        const name = $("#name").val();
        const quantity = $("#quantity").val();
        const price = $("#price").val(); 

        const data = {
            "order_id": parseInt(orderId),
            "item_name": name,
            "quantity": parseInt(quantity),
            "price": parseInt(price)
        };

        var ajax = $.ajax({
            type: "POST",
            url: `/orders/${orderId}/items`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done((res) => {
            updateItemFormData(res)
            flashMessage("Success")
        });

        ajax.fail(function(res){
            flashMessage(res.responseJSON.message)
        });
    });

    // ****************************************
    // Delete an Item
    // ****************************************

    $("#item-delete-btn").click(() => {
        const itemId = $("#item_id").val(); 
        const orderId = $("#item_order_id").val();

        if (!(itemId && orderId)) {
            alert("Please enter an Item ID and an Order ID."); 
            return; 
        }

        const ajax = $.ajax({
            type: "DELETE",
            url: `/orders/${orderId}/items/${itemId}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done((res) => {
            clearItemFormData()
            clearItemResults()
            flashMessage("Item has been Deleted!")
        });

        ajax.fail((res) => {
            flashMessage("Server error!")
        });
    });
})
