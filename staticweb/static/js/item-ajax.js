$(document).ready(function(){
	var page = 1;
	var current_page = 1;
	var total_page = 0;
	var is_ajax_fire = 0;

	manageData();

	// manage data list
	function manageData() {
		$.ajax({
			url: 'db/getData.php',
			dataType: 'json',
			data: {page:page}
		}).done(function(data){
			manageRow(data.data);
			is_ajax_fire = 1;
		});
	}

	// Get Page Data
	function getPageData() {
		$.ajax({
			url: 'db/getData.php',
			dataType: 'json',
			data: {page:page}
		}).done(function(data){
			manageRow(data.data);
		});
	}

	// Add New Item Table Row
	function manageRow(data) {
		var rows = '';
		$.each(data, function(key, value){
			rows = rows + '<tr>';
				rows = rows + '<td>' + value.judul + '</td>';
				rows = rows + '<td>' + value.pengarang + '</td>';
				rows = rows + '<td>' + value.ringkasan + '</td>';
				rows = rows + '<td data-id="' + value.id + '">';
					rows = rows + '<button data-toggle="modal" data-target="#edit-item" class="btn btn-primary edit-item">Edit</button>';
					rows = rows + '<button class="btn btn-danger remove-item">Delete</button>';
				rows = rows + '</td>';
			rows = rows + '</tr>'; 
		});
		$("tbody").html(rows);
	}

	// Create New Item
	$(".crud-submit").click(function(e){
		e.preventDefault();
		var form_action = $("#create-item").find("form").attr("action");
		var judul = $("#create-item").find("input[name='judul']").val();
		var pengarang = $("#create-item").find("input[name='pengarang']").val();
		var ringkasan = $("#create-item").find("textarea[name='ringkasan']").val();
		if (judul != '' && pengarang != '' && ringkasan != '') {
			$.ajax({
				dataType: 'json',
				type: 'POST',
				url: form_action,
				data: {judul:judul, pengarang:pengarang ,ringkasan:ringkasan}
			}).done(function(data){
				$("#create-item").find("input[name='judul']").val('');
				$("#create-item").find("input[name='pengarang']").val('');
				$("#create-item").find("textarea[name='ringkasan']").val('');
				getPageData();
				$(".modal").modal('hide');
				toastr.success('Item Created Successfully.', 'Success Alert', {timeOut: 5000});
			});
		} else {
			alert('You are missing title or description');
		}
	});

	// Remove Item
	$("body").on("click", ".remove-item", function(){
		var id = $(this).parent("td").data('id');
		var c_obj = $(this).parents("tr");

		$.ajax({
			dataType: 'json',
			type: 'POST',
			url: 'db/delete.php',
			data: {id:id}
		}).done(function(data){
			c_obj.remove();
			toastr.success('Item Deleted Successfully.', 'Success Alert', {timeOut: 5000});
			getPageData();
		});
	});

	// Edit Item
	$("body").on("click",".edit-item", function(){
		var id = $(this).parent('td').data('id');
		var judul = $(this).parent('td').prev('td').prev('td').prev('td').text();
		var pengarang = $(this).parent('td').prev('td').prev('td').text();
		var ringkasan = $(this).parent('td').prev('td').text();

		$("#edit-item").find("input[name='judul']").val(judul);
		$("#edit-item").find("input[name='pengarang']").val(pengarang);
		$("#edit-item").find("textarea[name='ringkasan']").val(ringkasan);
		$("#edit-item").find(".edit-id").val(id);
	});

	// Updated new Item
	$(".crud-submit-edit").click(function(e){
		e.preventDefault();
		var form_action = $("#edit-item").find("form").attr("action");
		var judul = $("#edit-item").find("input[name='judul']").val();
		var pengarang = $("#edit-item").find("input[name='pengarang']").val();
		var ringkasan = $("#edit-item").find("textarea[name='ringkasan']").val();
		var id = $("#edit-item").find(".edit-id").val();

		if (judul != '' && pengarang != '' && ringkasan != '') {
			$.ajax({
				dataType: 'json',
				type: 'POST',
				url: form_action,
				data: {judul:judul, pengarang:pengarang, ringkasan:ringkasan, id:id}
			}).done(function(data){
				getPageData();
				$(".modal").modal('hide');
				toastr.success('Item Updated Successfully.', 'Success Alert', {timeOut: 5000});
			});
		} else {
			alert('Anda lupa mengisi judul atau pengarang atau ringkasan.');
		}
	});
});