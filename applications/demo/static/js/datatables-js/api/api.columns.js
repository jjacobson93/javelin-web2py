

(/** @lends <global> */function() {

var _api = DataTable.Api;

var _setColumnVis = function ( settings, column, vis ) {
	var
		cols = settings.aoColumns,
		col  = cols[ column ],
		data = settings.aoData,
		row, cells, i, ien, tr;

	// Get
	if ( vis === undefined ) {
		return col.bVisible;
	}

	// Set
	// No change
	if ( col.bVisible === vis ) {
		return;
	}

	if ( vis ) {
		// Insert column
		// Need to decide if we should use appendChild or insertBefore
		var insertBefore = $.inArray( true, _pluck(cols, 'bVisible'), column+1 );

		for ( i=0, ien=data.length ; i<ien ; i++ ) {
			tr = data[i].nTr;
			cells = data[i].anCells;

			if ( tr ) {
				// insertBefore can act like appendChild if 2nd arg is null
				tr.insertBefore( cells[ column ], cells[ insertBefore ] || null );
			}
		}
	}
	else {
		// Remove column
		$( _pluck( settings.aoData, 'anCells', column ) ).remove();

		col.bVisible = false;
		_fnDrawHead( settings, settings.aoHeader );
		_fnDrawHead( settings, settings.aoFooter );

		_fnSaveState( settings );
	}

	// Common actions
	col.bVisible = vis;
	_fnDrawHead( settings, settings.aoHeader );
	_fnDrawHead( settings, settings.aoFooter );

	// Automatically adjust column sizing
	_fnAdjustColumnSizing( settings );

	// Realign columns for scrolling
	if ( settings.oScroll.sX || settings.oScroll.sY ) {
		_fnScrollDraw( settings );
	}

	_fnCallbackFire( settings, null, 'column-visibility', [settings, column, vis] );

	_fnSaveState( settings );
};


/**
 *
 */
_api.register( 'columns()', function ( selector, opts ) {
	// argument shifting
	if ( selector === undefined ) {
		selector = '';
	}
	else if ( $.isPlainObject( selector ) ) {
		opts = selector;
		selector = '';
	}

	opts = _selector_opts( opts );

	var inst = this.iterator( 'table', function ( settings ) {
		return _column_selector( settings, selector, opts );
	} );

	// Want argument shifting here and in _row_selector?
	inst.selector.cols = selector;
	inst.selector.opts = opts;

	return inst;
} );


/**
 *
 */
_api.registerPlural( 'columns().header()', 'column().header()', function ( selector, opts ) {
	return this.iterator( 'column', function ( settings, column ) {
		return settings.aoColumns[column].nTh;
	} );
} );


/**
 *
 */
_api.registerPlural( 'columns().data()', 'column().data()', function () {
	return this.iterator( 'column-rows', function ( settings, column, i, j, rows ) {
		var a = [];
		for ( var row=0, ien=rows.length ; row<ien ; row++ ) {
			a.push( _fnGetCellData( settings, rows[row], column, '' ) );
		}
		return a;
	} );
} );


_api.registerPlural( 'columns().cache()', 'column().cache()', function ( type ) {
	return this.iterator( 'column-rows', function ( settings, column, i, j, rows ) {
		return _pluck_order( settings.aoData, rows,
			type === 'filter' ? '_aFilterData' : '_aSortData', column
		);
	} );
} );


_api.registerPlural( 'columns().nodes()', 'columns().nodes()', function () {
	return this.iterator( 'column-rows', function ( settings, column, i, j, rows ) {
		return _pluck_order( settings.aoData, rows, 'anCells', column ) ;
	} );
} );



_api.registerPlural( 'columns().visible()', 'column().visible()', function ( vis ) {
	return this.iterator( 'column', function ( settings, column ) {
		return _setColumnVis( settings, column, vis );
	} );
} );



_api.registerPlural( 'columns().index()', 'column().index()', function ( type ) {
	return this.iterator( 'column', function ( settings, column ) {
		return type === 'visible' ?
			_fnColumnIndexToVisible( settings, column ) :
			column;
	} );
} );


// _api.register( 'columns().show()', function () {
// 	var selector = this.selector;
// 	return this.columns( selector.cols, selector.opts ).visible( true );
// } );


// _api.register( 'columns().hide()', function () {
// 	var selector = this.selector;
// 	return this.columns( selector.cols, selector.opts ).visible( false );
// } );



_api.register( 'columns.adjust()', function () {
	return this.iterator( 'table', function ( settings ) {
		_fnAdjustColumnSizing( settings );
	} );
} );


// Convert from one column index type, to another type
_api.register( 'column.index()', function ( type, idx ) {
	if ( this.context.length !== 0 ) {
		var ctx = this.context[0];

		if ( type === 'fromVisible' || type === 'toIndex' ) {
			return _fnColumnIndexToVisible( ctx, idx );
		}
		else if ( type === 'fromIndex' || type === 'toVisible' ) {
			return _fnVisibleToColumnIndex( ctx, idx );
		}
	}
} );



_api.register( 'column()', function ( selector, opts ) {
	return _selector_first( this.columns( selector, opts ) );
} );


}());

