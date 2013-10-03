
/**
 * Generate the node required for filtering text
 *  @returns {node} Filter control element
 *  @param {object} oSettings dataTables settings object
 *  @memberof DataTable#oApi
 */
function _fnFeatureHtmlFilter ( oSettings )
{
	var oPreviousSearch = oSettings.oPreviousSearch;

	var sSearchStr = oSettings.oLanguage.sSearch;
	sSearchStr = (sSearchStr.indexOf('_INPUT_') !== -1) ?
	  sSearchStr.replace('_INPUT_', '<input type="search" />') :
	  sSearchStr==="" ? '<input type="search" />' : sSearchStr+' <input type="search" />';

	var nFilter = document.createElement( 'div' );
	nFilter.className = oSettings.oClasses.sFilter;
	nFilter.innerHTML = '<label>'+sSearchStr+'</label>';
	if ( !oSettings.aanFeatures.f )
	{
		nFilter.id = oSettings.sTableId+'_filter';
	}

	var jqFilter = $('input[type="search"]', nFilter);

	// Store a reference to the input element, so other input elements could be
	// added to the filter wrapper if needed (submit button for example)
	nFilter._DT_Input = jqFilter[0];

	jqFilter.val( oPreviousSearch.sSearch.replace('"','&quot;') );
	jqFilter.bind( 'keyup.DT search.DT', function(e) {
		/* Update all other filter input elements for the new display */
		var n = oSettings.aanFeatures.f;
		var val = this.value==="" ? "" : this.value; // mental IE8 fix :-(

		/* Now do the filter */
		if ( val != oPreviousSearch.sSearch )
		{
			_fnFilterComplete( oSettings, {
				"sSearch": val,
				"bRegex": oPreviousSearch.bRegex,
				"bSmart": oPreviousSearch.bSmart ,
				"bCaseInsensitive": oPreviousSearch.bCaseInsensitive
			} );

			// Need to redraw, without resorting
			oSettings._iDisplayStart = 0;
			_fnDraw( oSettings );
		}
	} );

	jqFilter
		.attr('aria-controls', oSettings.sTableId)
		.bind( 'keypress.DT', function(e) {
			/* Prevent form submission */
			if ( e.keyCode == 13 )
			{
				return false;
			}
		}
	);

	// Update the input elements whenever the table is filtered
	$(oSettings.nTable).on( 'filter.DT', function () {
		try {
			// IE9 throws an 'unknown error' if document.activeElement is used
			// inside an iframe or frame...
			if ( this._DT_Input !== document.activeElement ) {
				jqFilter.val( oPreviousSearch.sSearch );
			}
		}
		catch ( e ) {
			jqFilter.val( oPreviousSearch.sSearch );
		}
	} );

	return nFilter;
}


/**
 * Filter the table using both the global filter and column based filtering
 *  @param {object} oSettings dataTables settings object
 *  @param {object} oSearch search information
 *  @param {int} [iForce] force a research of the master array (1) or not (undefined or 0)
 *  @memberof DataTable#oApi
 */
function _fnFilterComplete ( oSettings, oInput, iForce )
{
	var oPrevSearch = oSettings.oPreviousSearch;
	var aoPrevSearch = oSettings.aoPreSearchCols;
	var fnSaveFilter = function ( oFilter ) {
		/* Save the filtering values */
		oPrevSearch.sSearch = oFilter.sSearch;
		oPrevSearch.bRegex = oFilter.bRegex;
		oPrevSearch.bSmart = oFilter.bSmart;
		oPrevSearch.bCaseInsensitive = oFilter.bCaseInsensitive;
	};

	// Resolve any column types that are unknown due to addition or invalidation
	// @todo As per sort - can this be moved into an event handler?
	_fnColumnTypes( oSettings );

	/* In server-side processing all filtering is done by the server, so no point hanging around here */
	if ( !oSettings.oFeatures.bServerSide )
	{
		/* Global filter */
		_fnFilter( oSettings, oInput.sSearch, iForce, oInput.bRegex, oInput.bSmart, oInput.bCaseInsensitive );
		fnSaveFilter( oInput );

		/* Now do the individual column filter */
		for ( var i=0 ; i<aoPrevSearch.length ; i++ )
		{
			_fnFilterColumn( oSettings, aoPrevSearch[i].sSearch, i, aoPrevSearch[i].bRegex,
				aoPrevSearch[i].bSmart, aoPrevSearch[i].bCaseInsensitive );
		}

		/* Custom filtering */
		_fnFilterCustom( oSettings );
	}
	else
	{
		fnSaveFilter( oInput );
	}

	/* Tell the draw function we have been filtering */
	oSettings.bFiltered = true;
	$(oSettings.oInstance).trigger('filter', oSettings);
}


/**
 * Apply custom filtering functions
 *  @param {object} oSettings dataTables settings object
 *  @memberof DataTable#oApi
 */
function _fnFilterCustom( oSettings )
{
	var afnFilters = DataTable.ext.filter;
	var aiFilterColumns = _fnGetColumns( oSettings, 'bSearchable' );

	for ( var i=0, iLen=afnFilters.length ; i<iLen ; i++ )
	{
		var iCorrector = 0;
		for ( var j=0, jLen=oSettings.aiDisplay.length ; j<jLen ; j++ )
		{
			var iDisIndex = oSettings.aiDisplay[j-iCorrector];
			var bTest = afnFilters[i](
				oSettings,
				_fnGetRowData( oSettings, iDisIndex, 'filter', aiFilterColumns ),
				iDisIndex
			);

			/* Check if we should use this row based on the filtering function */
			if ( !bTest )
			{
				oSettings.aiDisplay.splice( j-iCorrector, 1 );
				iCorrector++;
			}
		}
	}
}


/**
 * Filter the table on a per-column basis
 *  @param {object} oSettings dataTables settings object
 *  @param {string} sInput string to filter on
 *  @param {int} iColumn column to filter
 *  @param {bool} bRegex treat search string as a regular expression or not
 *  @param {bool} bSmart use smart filtering or not
 *  @param {bool} bCaseInsensitive Do case insenstive matching or not
 *  @memberof DataTable#oApi
 */
function _fnFilterColumn ( settings, searchStr, colIdx, regex, smart, caseInsensitive )
{
	if ( searchStr === '' ) {
		return;
	}

	var data;
	var display = settings.aiDisplay;
	var rpSearch = _fnFilterCreateSearch( searchStr, regex, smart, caseInsensitive );

	for ( var i=display.length-1 ; i>=0 ; i-- ) {
		data = settings.aoData[ display[i] ]._aFilterData[ colIdx ];

		if ( ! rpSearch.test( data ) ) {
			display.splice( i, 1 );
		}
	}
}


/**
 * Filter the data table based on user input and draw the table
 *  @param {object} settings dataTables settings object
 *  @param {string} input string to filter on
 *  @param {int} force optional - force a research of the master array (1) or not (undefined or 0)
 *  @param {bool} regex treat as a regular expression or not
 *  @param {bool} smart perform smart filtering or not
 *  @param {bool} caseInsensitive Do case insenstive matching or not
 *  @memberof DataTable#oApi
 */
function _fnFilter( settings, input, force, regex, smart, caseInsensitive )
{
	var rpSearch = _fnFilterCreateSearch( input, regex, smart, caseInsensitive );
	var prevSearch = settings.oPreviousSearch.sSearch;
	var displayMaster = settings.aiDisplayMaster;
	var display, invalidated, i;

	// Need to take account of custom filtering functions - always filter
	if ( DataTable.ext.filter.length !== 0 ) {
		force = true;
	}

	// Check if any of the rows were invalidated
	invalidated = _fnFilterData( settings );

	// If the input is blank - we just want the full data set
	if ( input.length <= 0 ) {
		settings.aiDisplay = displayMaster.slice();
	}
	else {
		// New search - start from the master array
		if ( invalidated ||
			 force ||
			 prevSearch.length > input.length ||
			 input.indexOf(prevSearch) !== 0 )
		{
			settings.aiDisplay = displayMaster.slice();
		}

		// Search the display array
		display = settings.aiDisplay;

		for ( i=display.length-1 ; i>=0 ; i-- ) {
			if ( ! rpSearch.test( settings.aoData[ display[i] ]._sFilterRow ) ) {
				display.splice( i, 1 );
			}
		}
	}
}


/**
 * Build a regular expression object suitable for searching a table
 *  @param {string} sSearch string to search for
 *  @param {bool} bRegex treat as a regular expression or not
 *  @param {bool} bSmart perform smart filtering or not
 *  @param {bool} bCaseInsensitive Do case insensitive matching or not
 *  @returns {RegExp} constructed object
 *  @memberof DataTable#oApi
 */
function _fnFilterCreateSearch( sSearch, bRegex, bSmart, bCaseInsensitive )
{
	var asSearch,
		sRegExpString = bRegex ? sSearch : _fnEscapeRegex( sSearch );

	if ( bSmart )
	{
		/* Generate the regular expression to use. Something along the lines of:
		 * ^(?=.*?\bone\b)(?=.*?\btwo\b)(?=.*?\bthree\b).*$
		 */
		asSearch = sRegExpString.split( ' ' );
		sRegExpString = '^(?=.*?'+asSearch.join( ')(?=.*?' )+').*$';
	}

	return new RegExp( sRegExpString, bCaseInsensitive ? "i" : "" );
}


/**
 * scape a string such that it can be used in a regular expression
 *  @param {string} sVal string to escape
 *  @returns {string} escaped string
 *  @memberof DataTable#oApi
 */
function _fnEscapeRegex ( sVal )
{
	var acEscape = [ '/', '.', '*', '+', '?', '|', '(', ')', '[', ']', '{', '}', '\\', '$', '^', '-' ];
	var reReplace = new RegExp( '(\\' + acEscape.join('|\\') + ')', 'g' );
	return sVal.replace(reReplace, '\\$1');
}



var __filter_div = $('<div>');

// Update the filtering data for each row if needed (by invalidation or first run)
function _fnFilterData ( settings )
{
	var columns = settings.aoColumns;
	var column;
	var i, j, ien, jen, filterData, cellData, row;
	var fomatters = DataTable.ext.type.filter;
	var wasInvalidated = false;

	for ( i=0, ien=settings.aoData.length ; i<ien ; i++ ) {
		row = settings.aoData[i];

		if ( ! row._aFilterData ) {
			filterData = [];

			for ( j=0, jen=columns.length ; j<jen ; j++ ) {
				column = columns[j];

				if ( column.bSearchable ) {
					cellData = _fnGetCellData( settings, i, j, 'filter' );

					cellData = fomatters[ column.sType ] ?
						fomatters[ column.sType ]( cellData ) :
						cellData !== null ?
							cellData :
							'';
				}
				else {
					cellData = '';
				}

				// If it looks like there is an HTML entity in the string,
				// attempt to decode it so sorting works as expected
				if ( cellData.indexOf && cellData.indexOf('&') !== -1 ) {
					cellData = __filter_div.html( cellData ).text();
				}

				filterData.push( cellData );
			}

			row._aFilterData = filterData;
			row._sFilterRow = filterData.join('  ');
			wasInvalidated = true;
		}
	}

	return wasInvalidated;
}

