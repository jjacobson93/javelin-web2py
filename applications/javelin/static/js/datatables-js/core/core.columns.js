/**
 * Add a column to the list used for the table with default values
 *  @param {object} oSettings dataTables settings object
 *  @param {node} nTh The th element for this column
 *  @memberof DataTable#oApi
 */
function _fnAddColumn( oSettings, nTh )
{
	var oDefaults = DataTable.defaults.column;
	var iCol = oSettings.aoColumns.length;
	var oCol = $.extend( {}, DataTable.models.oColumn, oDefaults, {
		"sSortingClass": oSettings.oClasses.sSortable,
		"sSortingClassJUI": oSettings.oClasses.sSortJUI,
		"nTh": nTh ? nTh : document.createElement('th'),
		"sTitle":    oDefaults.sTitle    ? oDefaults.sTitle    : nTh ? nTh.innerHTML : '',
		"aDataSort": oDefaults.aDataSort ? oDefaults.aDataSort : [iCol],
		"mData": oDefaults.mData ? oDefaults.mData : iCol
	} );
	oSettings.aoColumns.push( oCol );

	/* Add a column specific filter */
	if ( oSettings.aoPreSearchCols[ iCol ] === undefined || oSettings.aoPreSearchCols[ iCol ] === null )
	{
		oSettings.aoPreSearchCols[ iCol ] = $.extend( true, {}, DataTable.models.oSearch );
	}
	else
	{
		var oPre = oSettings.aoPreSearchCols[ iCol ];

		/* Don't require that the user must specify bRegex, bSmart or bCaseInsensitive */
		if ( oPre.bRegex === undefined )
		{
			oPre.bRegex = true;
		}

		if ( oPre.bSmart === undefined )
		{
			oPre.bSmart = true;
		}

		if ( oPre.bCaseInsensitive === undefined )
		{
			oPre.bCaseInsensitive = true;
		}
	}

	/* Use the column options function to initialise classes etc */
	_fnColumnOptions( oSettings, iCol, null );
}


/**
 * Apply options for a column
 *  @param {object} oSettings dataTables settings object
 *  @param {int} iCol column index to consider
 *  @param {object} oOptions object with sType, bVisible and bSearchable etc
 *  @memberof DataTable#oApi
 */
function _fnColumnOptions( oSettings, iCol, oOptions )
{
	var oCol = oSettings.aoColumns[ iCol ];
	var oClasses = oSettings.oClasses;

	/* User specified column options */
	if ( oOptions !== undefined && oOptions !== null )
	{
		// Map camel case parameters to their Hungarian counterparts
		_fnCamelToHungarian( DataTable.defaults.column, oOptions );

		/* Backwards compatibility for mDataProp */
		if ( oOptions.mDataProp !== undefined && !oOptions.mData )
		{
			oOptions.mData = oOptions.mDataProp;
		}

		oCol._sManualType = oOptions.sType;

		// `class` is a reserved word in Javascript, so we need to provide
		// the ability to use a valid name for the camel case input
		if ( oOptions.className && ! oOptions.sClass )
		{
			oOptions.sClass = oOptions.className;
		}

		$.extend( oCol, oOptions );
		_fnMap( oCol, oOptions, "sWidth", "sWidthOrig" );

		/* iDataSort to be applied (backwards compatibility), but aDataSort will take
		 * priority if defined
		 */
		if ( oOptions.iDataSort !== undefined )
		{
			oCol.aDataSort = [ oOptions.iDataSort ];
		}
		_fnMap( oCol, oOptions, "aDataSort" );
	}

	/* Cache the data get and set functions for speed */
	var mDataSrc = oCol.mData;
	var mData = _fnGetObjectDataFn( mDataSrc );
	var mRender = oCol.mRender ? _fnGetObjectDataFn( oCol.mRender ) : null;

	var attrTest = function( src ) {
		return typeof src === 'string' && src.indexOf('@') !== -1;
	};
	oCol._bAttrSrc = $.isPlainObject( mDataSrc ) && (
		attrTest(mDataSrc.sort) || attrTest(mDataSrc.type) || attrTest(mDataSrc.filter)
	);

	oCol.fnGetData = function (oData, sSpecific) {
		var innerData = mData( oData, sSpecific );

		if ( oCol.mRender && (sSpecific && sSpecific !== '') )
		{
			return mRender( innerData, sSpecific, oData );
		}
		return innerData;
	};
	oCol.fnSetData = _fnSetObjectDataFn( mDataSrc );

	/* Feature sorting overrides column specific when off */
	if ( !oSettings.oFeatures.bSort )
	{
		oCol.bSortable = false;
	}

	/* Check that the class assignment is correct for sorting */
	var bAsc = $.inArray('asc', oCol.asSorting) !== -1;
	var bDesc = $.inArray('desc', oCol.asSorting) !== -1;
	if ( !oCol.bSortable || (!bAsc && !bDesc) )
	{
		oCol.sSortingClass = oClasses.sSortableNone;
		oCol.sSortingClassJUI = "";
	}
	else if ( bAsc && !bDesc )
	{
		oCol.sSortingClass = oClasses.sSortableAsc;
		oCol.sSortingClassJUI = oClasses.sSortJUIAscAllowed;
	}
	else if ( !bAsc && bDesc )
	{
		oCol.sSortingClass = oClasses.sSortableDesc;
		oCol.sSortingClassJUI = oClasses.sSortJUIDescAllowed;
	}
}


/**
 * Adjust the table column widths for new data. Note: you would probably want to
 * do a redraw after calling this function!
 *  @param {object} settings dataTables settings object
 *  @memberof DataTable#oApi
 */
function _fnAdjustColumnSizing ( settings )
{
	/* Not interested in doing column width calculation if auto-width is disabled */
	if ( settings.oFeatures.bAutoWidth !== false )
	{
		var columns = settings.aoColumns;

		_fnCalculateColumnWidths( settings );
		for ( var i=0 , iLen=columns.length ; i<iLen ; i++ )
		{
			columns[i].nTh.style.width = columns[i].sWidth;
		}
	}

	var scroll = settings.oScroll;
	if ( scroll.sY !== '' || scroll.sX !== '')
	{
		_fnScrollDraw( settings );
	}

	_fnCallbackFire( settings, null, 'column-sizing', [settings] );
}


/**
 * Covert the index of a visible column to the index in the data array (take account
 * of hidden columns)
 *  @param {object} oSettings dataTables settings object
 *  @param {int} iMatch Visible column index to lookup
 *  @returns {int} i the data index
 *  @memberof DataTable#oApi
 */
function _fnVisibleToColumnIndex( oSettings, iMatch )
{
	var aiVis = _fnGetColumns( oSettings, 'bVisible' );

	return typeof aiVis[iMatch] === 'number' ?
		aiVis[iMatch] :
		null;
}


/**
 * Covert the index of an index in the data array and convert it to the visible
 *   column index (take account of hidden columns)
 *  @param {int} iMatch Column index to lookup
 *  @param {object} oSettings dataTables settings object
 *  @returns {int} i the data index
 *  @memberof DataTable#oApi
 */
function _fnColumnIndexToVisible( oSettings, iMatch )
{
	var aiVis = _fnGetColumns( oSettings, 'bVisible' );
	var iPos = $.inArray( iMatch, aiVis );

	return iPos !== -1 ? iPos : null;
}


/**
 * Get the number of visible columns
 *  @param {object} oSettings dataTables settings object
 *  @returns {int} i the number of visible columns
 *  @memberof DataTable#oApi
 */
function _fnVisbleColumns( oSettings )
{
	return _fnGetColumns( oSettings, 'bVisible' ).length;
}


/**
 * Get an array of column indexes that match a given property
 *  @param {object} oSettings dataTables settings object
 *  @param {string} sParam Parameter in aoColumns to look for - typically
 *    bVisible or bSearchable
 *  @returns {array} Array of indexes with matched properties
 *  @memberof DataTable#oApi
 */
function _fnGetColumns( oSettings, sParam )
{
	var a = [];

	$.map( oSettings.aoColumns, function(val, i) {
		if ( val[sParam] ) {
			a.push( i );
		}
	} );

	return a;
}


function _fnColumnTypes ( settings )
{
	var columns = settings.aoColumns;
	var data = settings.aoData;
	var types = DataTable.ext.type.detect;
	var i, ien, j, jen, k, ken;
	var col, cell, detectedType, cache;

	// For each column, spin over the 
	for ( i=0, ien=columns.length ; i<ien ; i++ ) {
		col = columns[i];
		cache = [];

		if ( ! col.sType && col._sManualType ) {
			col.sType = col._sManualType;
		}
		else if ( ! col.sType ) {
			for ( j=0, jen=types.length ; j<jen ; j++ ) {
				for ( k=0, ken=data.length ; k<ken ; k++ ) {
					// Use a cache array so we only need to get the type data
					// from the formatter once (when using multiple detectors)
					if ( cache[k] === undefined ) {
						cache[k] = _fnGetCellData( settings, k, i, 'type' );
					}

					detectedType = types[j]( cache[k] );

					// Doesn't match, so break early, since this type can't
					// apply to this column. Also, HTML is a special case since
					// it is so similar to `string`. Just a single match is
					// needed for a column to be html type
					if ( ! detectedType || detectedType === 'html' ) {
						break;
					}
				}

				// Type is valid for all data points in the column - use this
				// type
				if ( detectedType ) {
					col.sType = detectedType;
					break;
				}
			}

			// Fall back - if no type was detected, always use string
			if ( ! col.sType ) {
				col.sType = 'string';
			}
		}
	}
}


/**
 * Take the column definitions and static columns arrays and calculate how
 * they relate to column indexes. The callback function will then apply the
 * definition found for a column to a suitable configuration object.
 *  @param {object} oSettings dataTables settings object
 *  @param {array} aoColDefs The aoColumnDefs array that is to be applied
 *  @param {array} aoCols The aoColumns array that defines columns individually
 *  @param {function} fn Callback function - takes two parameters, the calculated
 *    column index and the definition for that column.
 *  @memberof DataTable#oApi
 */
function _fnApplyColumnDefs( oSettings, aoColDefs, aoCols, fn )
{
	var i, iLen, j, jLen, k, kLen, def;

	// Column definitions with aTargets
	if ( aoColDefs )
	{
		/* Loop over the definitions array - loop in reverse so first instance has priority */
		for ( i=aoColDefs.length-1 ; i>=0 ; i-- )
		{
			def = aoColDefs[i];

			/* Each definition can target multiple columns, as it is an array */
			var aTargets = def.targets !== undefined ?
				def.targets :
				def.aTargets;

			if ( ! $.isArray( aTargets ) )
			{
				aTargets = [ aTargets ];
			}

			for ( j=0, jLen=aTargets.length ; j<jLen ; j++ )
			{
				if ( typeof aTargets[j] === 'number' && aTargets[j] >= 0 )
				{
					/* Add columns that we don't yet know about */
					while( oSettings.aoColumns.length <= aTargets[j] )
					{
						_fnAddColumn( oSettings );
					}

					/* Integer, basic index */
					fn( aTargets[j], def );
				}
				else if ( typeof aTargets[j] === 'number' && aTargets[j] < 0 )
				{
					/* Negative integer, right to left column counting */
					fn( oSettings.aoColumns.length+aTargets[j], def );
				}
				else if ( typeof aTargets[j] === 'string' )
				{
					/* Class name matching on TH element */
					for ( k=0, kLen=oSettings.aoColumns.length ; k<kLen ; k++ )
					{
						if ( aTargets[j] == "_all" ||
						     $(oSettings.aoColumns[k].nTh).hasClass( aTargets[j] ) )
						{
							fn( k, def );
						}
					}
				}
			}
		}
	}

	// Statically defined columns array
	if ( aoCols )
	{
		for ( i=0, iLen=aoCols.length ; i<iLen ; i++ )
		{
			fn( i, aoCols[i] );
		}
	}
}

