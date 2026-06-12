$( document ).ready(function() {
    $('#myTable').DataTable( {
        paging: true,
        dom: '<B>fltip',
        buttons: [
            'copy', 'excel', 'pdf','print',{
                extend:    'colvis',
                text:'Select Column',
                titleAttr: 'Column Visibility'
            }
        ],
        pagingType:'full_numbers',
        responsive: true,
        lengthMenu: [
            [5,10, 20, 35, -1],
            [5,10, 20, 35, ' All Records ']
        ],
       
    } );  
})
