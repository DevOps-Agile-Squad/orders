$(() => {
  // ****************************************
  //  U T I L I T Y   F U N C T I O N S
  // ****************************************

  // Updates the form with data from the response
  const updateOrderFormData = (res, method) => {
    console.log(res);
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
  };

  // Clears all form fields in Order form
  const clearOrderFormData = () => {
    const ids = ["order_id", "customer_id", "address", "search_value"];
    ids.forEach((id) => {
      $("#" + id).val("");
      $("#" + id).removeClass("is-invalid");
    });
    $("#status").val("Received");
  };

  // Changes the status bar message and styles
  const flashMessage = (message, type = "success") => {
    var wrapper = document.createElement("div");
    wrapper.innerHTML =
      '<div class="alert alert-' +
      type +
      ' alert-dismissible fade show shadow rounded" role="alert">' +
      '<svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Info:"><use xlink:href="#' +
      type +
      '-fill" /></svg>' +
      message +
      '<button type="button" class="btn-close" data-bs-dismiss="alert"></button></button></div>';

    // $("#liveAlertPlaceholder").append(wrapper);
    $("#status-bar")
      .removeClass(
        "alert-secondary alert-info alert-danger alert-success alert-warning"
      )
      .addClass(`alert-${type}`);
    $("#flash_message").empty();
    $("#flash_message").append(message);
    $("#status-icon").attr("xlink:href", "#" + type + "-fill");
    $(".alert-dismissible")
      .fadeTo(3500, 500)
      .slideUp(500, function () {
        $(this).remove();
      });
  };

  // Show warnings for missing fields
  const validateFields = (fields) => {
    var allValid = true;
    for (const field of fields) {
      if ($(`#${field}`).val() === "") {
        $(`#${field}`).toggleClass("is-invalid", true);
        allValid = false;
      } else {
        $(`#${field}`).toggleClass("is-invalid", false);
      }
    }
    return allValid;
  };

  // Clear search results for orders
  const clearOrderResults = () => {
    $("#search_value").empty();
    $("#search_results").empty();
  };

  // Reset the status bar
  const clearStatus = () => {
    $("#status-bar")
      .removeClass(
        "alert-secondary alert-info alert-danger alert-success alert-warning"
      )
      .addClass("alert-secondary");
    $("#flash_message").empty();
    $("#status-icon").attr("xlink:href", "#info-fill");
  };

  // List the orders received from a request
  const listOrders = (res, method) => {
    clearOrderResults();
    if (method === "list" || method === "search") {
      for (let order of res) {
        console.log(order);
        let itemsString = "";
        order.items.map((item) => {
          itemsString += `<tr><td style="width:3%">[${item.item_id}]</td><td style="width:12%">${item.item_name}</td><td style="width:5%">$${item.price}</td><td style="width:5%">X ${item.quantity}</td></tr>`;
        });
        const row =
          '<tr><th scope="row">' +
          order.id +
          "</th><td>" +
          order.customer_id +
          "</td><td>" +
          order.address +
          '</td><td style="width:auto"><table class="table table-sm table-responsive mb-0">' +
          itemsString +
          "</table>" +
          "</td><td>" +
          order.status +
          "</td></tr>";
        $("#search_results").append(row);
      }
    } else {
      let itemsString = "";
      res.items.map((item) => {
        itemsString += `<tr><td style="width:3%">[${item.item_id}]</td><td style="width:12%">${item.item_name}</td><td style="width:5%">$${item.price}</td><td style="width:5%">X ${item.quantity}</td></tr>`;
      });
      const row =
        '<tr><th scope="row">' +
        res.id +
        "</th><td>" +
        res.customer_id +
        "</td><td>" +
        res.address +
        '</td><td style="width:auto"><table class="table table-sm table-responsive mb-0">' +
        itemsString +
        "</table>" +
        "</td><td>" +
        res.status +
        "</td></tr>";
      $("#search_results").append(row);
    }
  };

  // Updates the Item form with data from the response
  const updateItemFormData = (res) => {
    $("#item_id").val(res.item_id);
    $("#item_order_id").val(res.order_id);
    $("#name").val(res.item_name);
    $("#quantity").val(res.quantity);
    $("#price").val(res.price);
  };

  // Clears all form fields in Item form
  const clearItemFormData = () => {
    $("#item_id").val("");
    $("#item_order_id").val("");
    $("#name").val("");
    $("#quantity").val("");
    $("#price").val("");
  };

  // Clear results for items
  const clearItemResults = () => {
    $("#item_search_results").empty();
  };

  // List the item(s) received from a request
  const listItem = (res) => {
    clearItemResults();
    const row =
      "<tr><td>" +
      res.item_id +
      "</td><td>" +
      res.order_id +
      "</td><td>" +
      res.item_name +
      "</td><td>" +
      res.quantity +
      "</td><td>" +
      res.price +
      "</td></tr>";
    $("#item_search_results").append(row);
  };

  // ****************************************
  // Create an Order
  // ****************************************
  $("#create-btn").click(() => {
    const customerId = $("#customer_id").val();
    const address = $("#address").val();
    const status = $("#status").val();

    // Check if all fields are filled
    const fields = ["customer_id", "address", "status"];
    if (!validateFields(fields)) {
      flashMessage("Please fill in all fields", "warning");
      return;
    }

    const data = {
      customer_id: parseInt(customerId),
      address: address,
      status: status,
      items: [],
    };

    var ajax = $.ajax({
      type: "POST",
      url: "/orders",
      contentType: "application/json",
      data: JSON.stringify(data),
    });

    ajax.done((res) => {
      updateOrderFormData(res, "create");
      listOrders(res, "create");
      flashMessage(`Success. Order with id [${res.id}] created.`);
    });

    ajax.fail(function (res) {
      flashMessage(res.responseJSON.message, "danger");
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

    // Check if orderId exist
    const fields = ["order_id"];
    if (!validateFields(fields)) {
      flashMessage("Please fill in all fields", "warning");
      return;
    }

    const ajax_get = $.ajax({
      type: "GET",
      url: "/orders/" + orderId,
      contentType: "application/json",
      data: "",
    });

    ajax_get.done((res_get) => {
      customerId = customerId === "" ? res_get.customer_id : customerId;
      address = address === "" ? res_get.address : address;
      console.log("[update] response is: ", res_get);
      const data = {
        customer_id: parseInt(customerId),
        address: address,
        status: status,
      };

      const _ajax = $.ajax({
        type: "PUT",
        url: "/orders/" + orderId,
        contentType: "application/json",
        data: JSON.stringify(data),
      });

      _ajax.done((res) => {
        updateOrderFormData(res, "update");
        listOrders(res, "update");
        flashMessage(`Success. Order with id [${res.id}] updated.`);
      });

      _ajax.fail((res) => {
        flashMessage(res.responseJSON.message, "danger");
      });
    });

    ajax_get.fail((res) => {
      flashMessage(res.responseJSON.message, "danger");
    });
  });

  // ****************************************
  // Retrieve an Order
  // ****************************************
  $("#retrieve-btn").click(() => {
    const orderId = $("#order_id").val();

    // check fields
    const fields = ["order_id"];
    if (!validateFields(fields)) {
      flashMessage("Please fill in all fields", "warning");
      return;
    }

    const ajax = $.ajax({
      type: "GET",
      url: "/orders/" + orderId,
      contentType: "application/json",
      data: "",
    });

    ajax.done((res) => {
      console.log(res);
      listOrders(res, "retrieve");
      updateOrderFormData(res, "retrieve");
      flashMessage(`Success. Order [${orderId}] retrieved.`, "success");
    });

    ajax.fail((res) => {
      console.log(res);
      clearOrderFormData();
      flashMessage(res.responseJSON.message, "danger");
    });
  });

  // ****************************************
  // Search an Order by Customer ID or Item
  // ****************************************
  $("#search-btn").click(() => {
    const field = $("input[name='search_field']:checked").val();
    const text = $("input[name='search_field']:checked").parent().text();
    const value = $("#search_value").val();

    // Check if all fields are filled
    const fields = ["search_field", "search_value"];
    if (!validateFields(fields)) {
      flashMessage("Please fill in all fields", "warning");
      return;
    }

    const ajax = $.ajax({
      type: "GET",
      url: `/orders?${field}=${value}`,
      contentType: "application/json",
      data: "",
    });

    ajax.done((res) => {
      if (res.length === 0) {
        flashMessage("No orders found.", "warning");
        clearOrderResults();
      } else {
        listOrders(res, "search");
        updateOrderFormData(res, "search");
        flashMessage(
          `Success. [${res.length}] orders with ${text}= ${value} found.`,
          "success"
        );
      }
    });

    ajax.fail((res) => {
      clearOrderFormData();
      flashMessage(res.responseJSON.message, "danger");
    });
  });

  // ****************************************
  // Delete an Order
  // ****************************************
  $("#delete-btn").click(() => {
    const orderId = $("#order_id").val();

    // check fields
    const fields = ["order_id"];
    if (!validateFields(fields)) {
      flashMessage("Please fill in all fields", "warning");
      return;
    }

    const ajax = $.ajax({
      type: "DELETE",
      url: "/orders/" + orderId,
      contentType: "application/json",
      data: "",
    });

    ajax.done((res) => {
      console.log(res);
      clearOrderFormData();
      clearOrderResults();
      flashMessage(`Order has been Deleted! ID: [${orderId}]`);
    });

    ajax.fail((res) => {
      console.log(res);
      flashMessage(res.responseJSON.message, "danger");
    });
  });

  // ****************************************
  // Cancel an order
  // ****************************************
  $("#cancel-btn").click(() => {
    console.log("Cancelling order");
    const orderId = $("#order_id").val();

    // check fields
    const fields = ["order_id"];
    if (!validateFields(fields)) {
      flashMessage("Please fill in all fields", "warning");
      return;
    }

    const ajax = $.ajax({
      type: "PUT",
      url: "/orders/" + orderId + "/cancel",
      contentType: "application/json",
      data: "",
    });

    ajax.done((res) => {
      clearOrderFormData();
      listOrders(res, "cancel");
      flashMessage(`Order has been Cancelled! ID: [${res.id}]`);
    });

    ajax.fail((res) => {
      flashMessage(
        "Order cannot be cancelled. " + res.responseJSON.message,
        "danger"
      );
    });
  });

  // ****************************************
  // Clear the Order form and status bar
  // ****************************************
  $("#clear-btn").click(() => {
    clearStatus();
    clearOrderFormData();
  });

  // ****************************************
  // List all orders
  // ****************************************
  $("#list-btn").click(() => {
    const ajax = $.ajax({
      type: "GET",
      url: "/orders",
      contentType: "application/json",
      data: "",
    });

    ajax.done((res) => {
      listOrders(res, "list");
      flashMessage(`Success. List returns [${res.length}] order(s).`);
    });
  });

  // ****************************************
  // Clear the Item form
  // ****************************************
  $("#item-clear-btn").click(() => {
    clearStatus();
    clearItemFormData();
  });

  // ****************************************
  // Retrieve an Item
  // ****************************************
  $("#item-retrieve-btn").click(() => {
    const itemId = $("#item_id").val();
    const orderId = $("#item_order_id").val();

    // check fields
    const fields = ["item_id", "item_order_id"];
    if (!validateFields(fields)) {
      flashMessage("Please fill in all fields", "warning");
      return;
    }

    const ajax = $.ajax({
      type: "GET",
      url: `/orders/${orderId}/items/${itemId}`,
      contentType: "application/json",
      data: "",
    });

    ajax.done((res) => {
      clearItemResults();
      listItem(res);
      updateItemFormData(res);
      flashMessage(`Success. Item [${itemId}] retrieved.`);
    });

    ajax.fail(function (res) {
      clearItemFormData();
      flashMessage(res.responseJSON.message, "danger");
    });
  });

  // ****************************************
  // Create an Item
  // ****************************************
  $("#item-create-btn").click(() => {
    const orderId = $("#item_order_id").val();
    const name = $("#name").val();
    const quantity = $("#quantity").val();
    const price = $("#price").val();

    // check fields
    const fields = ["item_order_id", "name", "quantity", "price"];
    if (!validateFields(fields)) {
      flashMessage("Please fill in all fields", "warning");
      return;
    }

    // check negative quantity, price
    if (quantity < 0) {
      flashMessage("Quantity cannot be negative", "warning");
      $("#quantity").addClass("is-invalid");
      return;
    } else {
      $("#quantity").removeClass("is-invalid");
    }
    if (price < 0) {
      flashMessage("Price cannot be negative", "warning");
      $("#price").addClass("is-invalid");
      return;
    } else {
      $("#price").removeClass("is-invalid");
    }

    const data = {
      order_id: parseInt(orderId),
      item_name: name,
      quantity: parseInt(quantity),
      price: parseFloat(price),
    };

    var ajax = $.ajax({
      type: "POST",
      url: `/orders/${orderId}/items`,
      contentType: "application/json",
      data: JSON.stringify(data),
    });

    ajax.done((res) => {
      clearItemResults();
      listItem(res);
      updateItemFormData(res);
      flashMessage(`Success. Item [${res.item_id}] ${res.item_name} created.`);
    });

    ajax.fail(function (res) {
      flashMessage(res.responseJSON.message, "danger");
    });
  });

  // ****************************************
  // Delete an Item
  // ****************************************
  $("#item-delete-btn").click(() => {
    const itemId = $("#item_id").val();
    const orderId = $("#item_order_id").val();

    // check fields
    const fields = ["item_id", "item_order_id"];
    if (!validateFields(fields)) {
      flashMessage("Please fill in all fields", "warning");
      return;
    }

    const ajax = $.ajax({
      type: "DELETE",
      url: `/orders/${orderId}/items/${itemId}`,
      contentType: "application/json",
      data: "",
    });

    ajax.done((res) => {
      clearItemFormData();
      clearItemResults();
      flashMessage(`Success. Item [${itemId}] in Order [${orderId}] deleted.`);
    });

    ajax.fail((res) => {
      flashMessage(res.responseJSON.message, "danger");
    });
  });
});
