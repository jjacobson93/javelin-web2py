

/**
 * Create an Ajax call based on the table's settings, taking into account that
 * parameters can have multiple forms, and backwards compatibility.
 *
 * @param {object} oSettings dataTables settings object
 * @param {array} data Data to send to the server, required by
 *     DataTables - may be augmented by developer callbacks
 * @param {function} fn Callback function to run when data is obtained
 */
function _fnBuildAjax( oSettings, data, fn )
{
	// Compatibility with 1.9-, allow fnServerData and event to manipulate
	_fnCallbackFire( oSettings, 'aoServerParams', 'serverParams', [data] );

	// Convert to object based for 1.10+
	var tmp = {};
	$.each( data, function (key, val) {
		tmp[val.name] = val.value;
	} );
	data = tmp;

	var ajaxData;
	var ajax = oSettings.ajax;
	var instance = oSettings.oInstance;

	if ( $.isPlainObject( ajax ) && ajax.data )
	{
		ajaxData = ajax.data;

		var newData = $.isFunction( ajaxData ) ?
			ajaxData( data ) :  // fn can manipulate data or return an object
			ajaxData;           // object or array to merge

		// If the function returned an object, use that alone
		data = $.isFunction( ajaxData ) && newData ?
			newData :
			$.extend( true, data, newData );

		// Remove the data property as we've resolved it already and don't want
		// jQuery to do it again (it is restored at the end of the function)
		delete ajax.data;
	}

	var baseAjax = {
		"data": data,
		"success": function (json) {
			if ( json.sError ) {
				oSettings.oApi._fnLog( oSettings, 0, json.sError );
			}

			$(instance).trigger('xhr', [oSettings, json]);
			fn( json );
		},
		"dataType": "json",
		"cache": false,
		"type": oSettings.sServerMethod,
		"error": function (xhr, error, thrown) {
			if ( error == "parsererror" ) {
				oSettings.oApi._fnLog( oSettings, 0, 'Invalid JSON response', 1 );
			}
		}
	};

	if ( oSettings.fnServerData )
	{
		// DataTables 1.9- compatibility
		oSettings.fnServerData.call( instance,
			oSettings.sAjaxSource, data, fn, oSettings
		);
	}
	else if ( oSettings.sAjaxSource || typeof ajax === 'string' )
	{
		// DataTables 1.9- compatibility
		oSettings.jqXHR = $.ajax( $.extend( baseAjax, {
			url: ajax || oSettings.sAjaxSource
		} ) );
	}
	else if ( $.isFunction( ajax ) )
	{
		// Is a function - let the caller define what needs to be done
		oSettings.jqXHR = ajax.call( instance, data, fn, oSettings );
	}
	else
	{
		// Object to extend the base settings
		oSettings.jqXHR = $.ajax( $.extend( baseAjax, ajax ) );

		// Restore for next time around
		ajax.data = ajaxData;
	}
}


/**
 * Update the table using an Ajax call
 *  @param {object} oSettings dataTables settings object
 *  @returns {boolean} Block the table drawing or not
 *  @memberof DataTable#oApi
 */
function _fnAjaxUpdate( oSettings )
{
	if ( oSettings.bAjaxDataGet )
	{
		oSettings.iDraw++;
		_fnProcessingDisplay( oSettings, true );
		var iColumns = oSettings.aoColumns.length;
		var aoData = _fnAjaxParameters( oSettings );

		_fnBuildAjax( oSettings, aoData, function(json) {
			_fnAjaxUpdateDraw( oSettings, json );
		}, oSettings );

		return false;
	}
	return true;
}


/**
 * Build up the parameters in an object needed for a server-side processing request
 *  @param {object} oSettings dataTables settings object
 *  @returns {bool} block the table drawing or not
 *  @memberof DataTable#oApi
 */
function _fnAjaxParameters( oSettings )
{
	var aoColumns = oSettings.aoColumns;
	var iColumns = aoColumns.length;
	var aoData = [], mDataProp, aaSort, aDataSort;
	var i, j;
	var param = function ( name, value ) {
		aoData.push( { 'name': name, 'value': value } );
	};

	param( 'sEcho',          oSettings.iDraw );
	param( 'iColumns',       iColumns );
	param( 'sColumns',       _pluck( aoColumns, 'sName' ).join(',') );
	param( 'iDisplayStart',  oSettings._iDisplayStart );
	param( 'iDisplayLength', oSettings.oFeatures.bPaginate !== false ?
		oSettings._iDisplayLength : -1
	);

	for ( i=0 ; i<iColumns ; i++ )
	{
		mDataProp = aoColumns[i].mData;
		param( "mDataProp_"+i, typeof(mDataProp)==="function" ? 'function' : mDataProp );
	}

	/* Filtering */
	if ( oSettings.oFeatures.bFilter !== false )
	{
		param( 'sSearch', oSettings.oPreviousSearch.sSearch );
		param( 'bRegex', oSettings.oPreviousSearch.bRegex );
		for ( i=0 ; i<iColumns ; i++ )
		{
			param( 'sSearch_'+i,     oSettings.aoPreSearchCols[i].sSearch );
			param( 'bRegex_'+i,      oSettings.aoPreSearchCols[i].bRegex );
			param( 'bSearchable_'+i, aoColumns[i].bSearchable );
		}
	}

	/* Sorting */
	if ( oSettings.oFeatures.bSort !== false )
	{
		var iCounter = 0;

		aaSort = ( oSettings.aaSortingFixed !== null ) ?
			oSettings.aaSortingFixed.concat( oSettings.aaSorting ) :
			oSettings.aaSorting.slice();

		for ( i=0 ; i<aaSort.length ; i++ )
		{
			aDataSort = aoColumns[ aaSort[i][0] ].aDataSort;

			for ( j=0 ; j<aDataSort.length ; j++ )
			{
				param( 'iSortCol_'+iCounter, aDataSort[j] );
				param( 'sSortDir_'+iCounter, aaSort[i][1] );
				iCounter++;
			}
		}
		param( 'iSortingCols', iCounter );

		for ( i=0 ; i<iColumns ; i++ )
		{
			param( 'bSortable_'+i, aoColumns[i].bSortable );
		}
	}

	return aoData;
}


/**
 * Data the data from the server (nuking the old) and redraw the table
 *  @param {object} oSettings dataTables settings object
 *  @param {object} json json data return from the server.
 *  @param {string} json.sEcho Tracking flag for DataTables to match requests
 *  @param {int} json.iTotalRecords Number of records in the data set, not accounting for filtering
 *  @param {int} json.iTotalDisplayRecords Number of records in the data set, accounting for filtering
 *  @param {array} json.aaData The data to display on this page
 *  @param {string} [json.sColumns] Column ordering (sName, comma separated)
 *  @memberof DataTable#oApi
 */
function _fnAjaxUpdateDraw ( oSettings, json )
{
	if ( json.sEcho !== undefined )
	{
		/* Protect against old returns over-writing a new one. Possible when you get
		 * very fast interaction, and later queries are completed much faster
		 */
		if ( json.sEcho*1 < oSettings.iDraw )
		{
			return;
		}
		oSettings.iDraw = json.sEcho * 1;
	}

	if ( !oSettings.oScroll.bInfinite || oSettings.bSorted || oSettings.bFiltered )
	{
		_fnClearTable( oSettings );
	}
	oSettings._iRecordsTotal = parseInt(json.iTotalRecords, 10);
	oSettings._iRecordsDisplay = parseInt(json.iTotalDisplayRecords, 10);

	var aData = _fnAjaxDataSrc( oSettings, json );
	for ( var i=0, iLen=aData.length ; i<iLen ; i++ )
	{
		_fnAddData( oSettings, aData[i] );
	}
	oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();

	oSettings.bAjaxDataGet = false;
	_fnDraw( oSettings );

	if ( ! oSettings._bInitComplete )
	{
		_fnInitComplete( oSettings, json );
	}

	oSettings.bAjaxDataGet = true;
	_fnProcessingDisplay( oSettings, false );
}


/**
 * Get the data from the JSON data source to use for drawing a table. Using
 * `_fnGetObjectDataFn` allows the data to be sourced from a property of the
 * source object, or from a processing function.
 *  @param {object} oSettings dataTables settings object
 *  @param  {object} json Data source object / array from the server
 *  @return {array} Array of data to use
 */
function _fnAjaxDataSrc ( oSettings, json )
{
	// @todo data and callback to aaData
	var dataSrc = $.isPlainObject( oSettings.ajax ) && oSettings.ajax.dataSrc !== undefined ?
		oSettings.ajax.dataSrc :
		oSettings.sAjaxDataProp; // Compatibility with 1.9-.

	return dataSrc !== "" ?
		_fnGetObjectDataFn( dataSrc )(json) :
		json;
}

