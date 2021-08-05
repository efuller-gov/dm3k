/**
 *  Module captures the lower level functions to place DM3K nodes and edges on the graph
 *
 *     DEPENDS ON:  mxgraph  (mxClient.min.js see https://jgraph.github.io/mxgraph)
 */


/**
 *  Adds a resource or activity block to the DM3K graph
 *
 *  @param (mxGraph) graph: an mxGraph object (e.g var graph = new mxGraph(container);)
 *  @param (string) typeName: the name of the type of block (this name is text at top of block)
 *  @param (string) blockName: the name of the block (this is name in text in the middle of block)
 *  @param (int) xLoc: the x-location of block on the graph
 *  @param (int) yLoc: the y-location of block on the graph
 *  @param (string) infoIcon: the folder path to the info-icon graphic
 *
 *  @return (mxCell) block: a vertex in the mxGraph representing an activity or resource
 */
function addDM3KResAct(container, graph, isResource, typeName, blockName, xLoc, yLoc, infoIcon, color) {
    const width = 150;
    const height = 100;
    const blockStyle = 'fontStyle=1;fontColor=#707070;fontSize=20;fillColor='+color+';strokeColor=#E9EDF2';
    const typeStyle = 'fontStyle=2;fontColor=#707070;fontSize=12;';
    const typeSize = 0;
    const typeXLoc = 0.5;
    const typeYLoc = 0.05;
    const infoIconSize = 25;
    const infoIconX = -15;
    const infoIconY = -15;
    const infoToolTip = 'click for instance information'

    var block = null;

    // Gets the default parent for inserting new cells. This
	// is normally the first child of the root (ie. layer 0).
	var parent = graph.getDefaultParent();

    // Adds cells to the model in a single step
	graph.getModel().beginUpdate();
	try
	{
	    block = graph.insertVertex(parent, typeName, blockName, xLoc, yLoc, width, height, blockStyle);
		var typeLabel = graph.insertVertex(block, blockName, typeName, typeXLoc, typeYLoc, typeSize, typeSize, typeStyle, true);
		var iCircle = new mxCellOverlay(new mxImage(infoIcon, infoIconSize, infoIconSize), infoToolTip);

		// the overlay point to be within the resource box
		var pt = iCircle.offset;
		pt.x = infoIconX;
		pt.y = infoIconY;
		graph.addCellOverlay(block,iCircle);

		// detect click on the circle-i
		iCircle.addListener(mxEvent.CLICK, function(sender, evt) 
		{
			var cell = evt.getProperty('cell');
			var cellType = 'Activity';
			var budgetName = [];
			var costName = [];
			var rewardName = ''

			if (isResource) {
				cellType = 'Resource';
				
				connectedBoxIDs = cell.edges.map(x=>x.target.getId());  // dont think reward and cost use cell.id like act and res!!!
				connectedBoxNames = cell.edges.map(x=>x.target.getValue());
				for (i=0; i< connectedBoxIDs.length; i++) {
					if (connectedBoxIDs[i].startsWith('budget')) {
						budgetName.push(connectedBoxNames[i]);
					}
				}
				


			} else {
				cellType = 'Activity';
				
				connectedBoxIDs = cell.edges.map(x=>x.target.getId());  // dont think reward and cost use cell.id like act and res!!!
				connectedBoxNames = cell.edges.map(x=>x.target.getValue());
				
				for (i=0; i< connectedBoxIDs.length; i++) {
					if (connectedBoxIDs[i].startsWith('reward')) {
						rewardName = connectedBoxNames[i];
					}
					if (connectedBoxIDs[i].startsWith('cost')) {
						costName.push(connectedBoxNames[i]);
					}
				}

			}
			var event = new CustomEvent(
				'CircleIClicked',
				{
					detail: {
						id: cell.id,
						name: cell.value,
						type: cellType,
						budget: budgetName,
						cost: costName,
						reward: rewardName
					},
					bubbles: true,
					cancelable: true
				
				}
			);
			container.dispatchEvent(event)
		});
	}
	finally
	{
	     // Update the display
	     graph.getModel().endUpdate();
	}

	return block;
}

/**
 *  Adds a budget block to the DM3K graph
 *
 *  @param (mxGraph) graph: an mxGraph object (e.g var graph = new mxGraph(container);)
 *  @param (string) budgetName: the name of the budget block (this is name in text in the middle of block)
 *  @param (mxCell) res: a vertex in the mxGraph representing a resource
 *
 *  @return (mxCell) block: a vertex in the mxGraph representing a budget
 */
function addDM3KBudget(graph, budgetName, res, budgetNum) {
    const width = 85;
    const height = 60;
    const space = 20;  // space between budget and resource
    const blockStyle = 'fontStyle=1;fontColor=#707070;fontSize=14;fillColor=#E9EDF2;strokeColor=#E9EDF2;';
    const typeStyle = 'fontStyle=2;fontColor=#707070;fontSize=10;';
    const typeSize = 0;
    const typeXLoc = 0.5;
    const typeYLoc = 0.05;
    const edgeStyle = 'defaultEdge;endArrow=none;startArrow=none;strokeColor=darkgray;strokeWidth=2;';

    // place the budget to the left of the resource
    // get the location of the resource
    var xLoc = res.geometry.x - space - width;
	var yLoc = res.geometry.y + budgetNum * (space + height);

    var block = null;

    // Gets the default parent for inserting new cells. This
	// is normally the first child of the root (ie. layer 0).
	var parent = graph.getDefaultParent();

    // Adds cells to the model in a single step
	graph.getModel().beginUpdate();
	try
	{
	    block = graph.insertVertex(parent, 'budget.'+budgetName+'.'+budgetNum, budgetName, xLoc, yLoc, width, height, blockStyle);
		var typeLabel = graph.insertVertex(block, null, 'budget', typeXLoc, typeYLoc, typeSize, typeSize, typeStyle, true);

		link = graph.insertEdge(parent, null, '', res, block, edgeStyle);

	}
	finally
	{
	     // Update the display
	     graph.getModel().endUpdate();
	}

	return block;
}

/**
 *  Adds a cost block to the DM3K graph
 *
 *  @param (mxGraph) graph: an mxGraph object (e.g var graph = new mxGraph(container);)
 *  @param (string) costName: the name of the cost block (this is name in text in the middle of block)
 *  @param (mxCell) act: a vertex in the mxGraph representing a activity
 *
 *  @return (mxCell) block: a vertex in the mxGraph representing a cost
 */
function addDM3KCost(graph, costName, act, costNum) {
    const width = 65;
    const height = 40;
    const space = 20;  // space between cost and activity
    const blockStyle = 'fontStyle=1;fontColor=#707070;fontSize=10;fillColor=#F2EFE9;strokeColor=#F2EFE9;';
    const typeStyle = 'fontStyle=2;fontColor=#707070;fontSize=8;';
    const typeSize = 0;
    const typeXLoc = 0.5;
    const typeYLoc = 0.05;
    const edgeStyle = 'defaultEdge;endArrow=none;startArrow=none;strokeColor=darkgray;strokeWidth=2;';

    // place the budget to the right of the activity near the top
    //var xLoc = act.geometry.x + act.geometry.width + space;
    //var yLoc = act.geometry.y;

    var xLoc = act.geometry.x + act.geometry.width + space;
    var yLoc = act.geometry.y + height + space + (height+space/2)*costNum;

    var block = null;

    // Gets the default parent for inserting new cells. This
	// is normally the first child of the root (ie. layer 0).
	var parent = graph.getDefaultParent();

	// Adds cells to the model in a single step
	graph.getModel().beginUpdate();
	try
	{
	    block = graph.insertVertex(parent, 'cost.'+costName+'.'+costNum, costName, xLoc, yLoc, width, height, blockStyle);
		var typeLabel = graph.insertVertex(block, null, 'cost', typeXLoc, typeYLoc, typeSize, typeSize, typeStyle, true);

		link = graph.insertEdge(parent, null, '', act, block, edgeStyle);

	}
	finally
	{
	     // Update the display
	     graph.getModel().endUpdate();
	}
	// This is a bug fix. Manually setting the id.
	block.setId('cost')
	return block;
}

/**
 *  Adds a reward block to the DM3K graph
 *
 *  @param (mxGraph) graph: an mxGraph object (e.g var graph = new mxGraph(container);)
 *  @param (string) rewardName: the name of the reward block (this is name in text in the middle of block)
 *  @param (mxCell) act: a vertex in the mxGraph representing a activity
 *
 *  @return (mxCell) block: a vertex in the mxGraph representing a reward
 */
function addDM3KReward(graph,rewardName, act) {
    const width = 65;
    const height = 40;
    const space = 20;  // space between cost and activity
    const blockStyle = 'fontStyle=1;fontColor=#707070;fontSize=10;fillColor=#F2EFE9;strokeColor=#F2EFE9;';
    const typeStyle = 'fontStyle=2;fontColor=#707070;fontSize=8;';
    const typeSize = 0;
    const typeXLoc = 0.5;
    const typeYLoc = 0.05;
    const edgeStyle = 'defaultEdge;endArrow=none;startArrow=none;strokeColor=darkgray;strokeWidth=2;';

    // place the reward to the right of the resource near the bottom
    var xLoc = act.geometry.x + act.geometry.width + space;
    var yLoc = act.geometry.y - height/4 + space/2;

    var block = null;

    // Gets the default parent for inserting new cells. This
	// is normally the first child of the root (ie. layer 0).
	var parent = graph.getDefaultParent();

    // Adds cells to the model in a single step
	graph.getModel().beginUpdate();
	try
	{
	    block = graph.insertVertex(parent, 'reward.'+act.getValue()+'.'+rewardName, rewardName, xLoc, yLoc, width, height, blockStyle);
		var typeLabel = graph.insertVertex(block, null, 'reward', typeXLoc, typeYLoc, typeSize, typeSize, typeStyle, true);

		link = graph.insertEdge(parent, null, '', act, block, edgeStyle);

	}
	finally
	{
	     // Update the display
	     graph.getModel().endUpdate();
	}
	block.setId('reward')
	return block;
}


/**
 *  Adds a 'can be allocated to' edge between two blocks
 *
 *  @param (mxGraph) graph: an mxGraph object (e.g var graph = new mxGraph(container);)
 *  @param (mxCell) res: a vertex in the mxGraph representing a resource
 *  @param (mxCell) act: a vertex in the mxGraph representing an activity
 *  @param (string) infoIcon: the folder path to the info-icon graphic
 *
 *  @return (mxCell) edge: an edge in the mxGraph representing the 'can be allocated to' link
 */
function addDM3KAllocatedEdge(container, graph, res, act, infoIcon) {
    const edgeStyle = 'defaultEdge;verticalAlign=bottom;verticalLabelPosition=top;fontColor=#707070;strokeColor=darkgray;strokeWidth=2;';
    const infoIconSize = 15;
    const infoIconX = 60;
    const infoIconY = -10;
    const infoToolTip = 'click for instance information'

    var edge = null;

    // Gets the default parent for inserting new cells. This
	// is normally the first child of the root (ie. layer 0).
	var parent = graph.getDefaultParent();

    // Adds cells to the model in a single step
	graph.getModel().beginUpdate();
	try
	{
	    edge = graph.insertEdge(parent, null, 'can be allocated to', res, act, edgeStyle)
		var iCircle = new mxCellOverlay(new mxImage(infoIcon, infoIconSize, infoIconSize), infoToolTip);
		var pt = iCircle.offset;
		pt.x = infoIconX;
		pt.y = infoIconY;
		graph.addCellOverlay(edge, iCircle);

		// Adds animation to edge shape and makes "pipe" visible
		//dm3kgraph.state.shape.node.getElementsByTagName('path')[0].removeAttribute('visibility');
		//dm3kgraph.state.shape.node.getElementsByTagName('path')[0].setAttribute('stroke-width', '6');
		//dm3kgraph.state.shape.node.getElementsByTagName('path')[0].setAttribute('stroke', 'lightGray');
		edge.setAttribute('class', 'flow');

		// detect click on the circle-i
		iCircle.addListener(mxEvent.CLICK, function(sender, evt)
		{
			var cell = evt.getProperty('cell');
			
			var event = new CustomEvent(
				'CircleIClicked',
				{
					detail: {
						id: cell.id,
						name: cell.source.value+"_"+cell.target.value,
						type: 'AllocatedTo',
						resourceName: cell.source.value,
						activityName: cell.target.value
					},
					bubbles: true,
					cancelable: true
				}
			);
			container.dispatchEvent(event)

		});

	}
	finally
	{
	     // Update the display
	     graph.getModel().endUpdate();
	}

	return edge;
}

/**
 *  Adds a 'contains' edge between two blocks
 *
 *  @param (mxGraph) graph: an mxGraph object (e.g var graph = new mxGraph(container);)
 *  @param (mxCell) parentBlock: a vertex in the mxGraph representing a resource or activity that is parent or container
 *  @param (mxCell) childBlock: a vertex in the mxGraph representing a resource or activity that is child on thing contained
 *  @param (string) infoIcon: the folder path to the info-icon graphic
 *
 *  @return (mxCell) edge: an edge in the mxGraph representing the 'can be allocated to' link
 */
function addDM3KContainsEdge(container, graph, parentBlock, childBlock, infoIcon) {
    const edgeStyle = 'defaultEdge;verticalAlign=bottom;verticalLabelPosition=top;fontColor=#707070;strokeColor=darkgray;strokeWidth=2;';
    const infoIconSize = 15;
    const infoIconX = 30;
    const infoIconY = -10;
    const infoToolTip = 'click for instance information'

    var edge = null;

    // Gets the default parent for inserting new cells. This
	// is normally the first child of the root (ie. layer 0).
	var parent = graph.getDefaultParent();

    // Adds cells to the model in a single step
	graph.getModel().beginUpdate();
	try
	{
	    edge = graph.insertEdge(parent, null, 'contains', parentBlock, childBlock, edgeStyle)
		var iCircle = new mxCellOverlay(new mxImage(infoIcon, infoIconSize, infoIconSize), infoToolTip);
		var pt = iCircle.offset;
		pt.x = infoIconX;
		pt.y = infoIconY;
		graph.addCellOverlay(edge, iCircle);

		// detect click on the circle-i
		iCircle.addListener(mxEvent.CLICK, function(sender, evt)
		{
			var cell = evt.getProperty('cell');
			
			var event = new CustomEvent(
				'CircleIClicked',
				{
					detail: {
						id: cell.id,
						name: cell.source.value+"_"+cell.target.value,
						type: 'Contains',
						parentName: cell.source.value,
						childName: cell.target.value
					},
					bubbles: true,
					cancelable: true
				}
			);
			container.dispatchEvent(event)

		});
	}
	finally
	{
	     // Update the display
	     graph.getModel().endUpdate();
	}

	return edge;
}

function addDM3KConstraintEdge(container, graph, allocatedLink1, allocatedLink2, constraintType) {
	//const edgeStyle = 'defaultEdge;verticalAlign=bottom;verticalLabelPosition=top;fontColor=#707070;strokeColor=blue;strokeWidth=2;';
	const edgeStyle = 'defaultEdge';
	const infoIconSize = 15;
    
    var edge = null;

    // Gets the default parent for inserting new cells. This
	// is normally the first child of the root (ie. layer 0).
	var parent = graph.getDefaultParent();

    // Adds cells to the model in a single step
	graph.getModel().beginUpdate();
	try
	{
		edge = graph.insertEdge(parent, null, constraintType, allocatedLink1, allocatedLink2, edgeStyle)
		
		// properties for Edge
		graph.setCellStyles(mxConstants.STYLE_STROKECOLOR, 'blue', [edge] )  // make the line color blue
		graph.setCellStyles(mxConstants.STYLE_STROKEWIDTH, 1, [edge] )  // stroke size in pixels
		graph.setCellStyles(mxConstants.STYLE_DASHED, 1, [edge] )   // set to dashed
		graph.setCellStyles(mxConstants.ARROW_SIZE, 20, [edge] )  // make the arrow smaller (default = 30)
		graph.setCellStyles(mxConstants.STYLE_ENDARROW, mxConstants.ARROW_OPEN, [edge] ) 
		graph.setCellStyles(mxConstants.STYLE_STARTARROW, mxConstants.ARROW_OVAL, [edge] ) 
		
		// properties for label
		graph.setCellStyles(mxConstants.STYLE_FONTCOLOR, 'blue', [edge] ) 
		graph.setCellStyles(mxConstants.STYLE_FONTSIZE, 9, [edge] )    // fontsize in pixels
		graph.setCellStyles(mxConstants.STYLE_VERTICAL_ALIGN, mxConstants.ALIGN_TOP, [edge] )  // how is label aligned vertically, set to top
		graph.setCellStyles(mxConstants.STYLE_ALIGN, mxConstants.ALIGN_LEFT, [edge] )  // how is label aligned horizontally, set to left
		graph.setCellStyles(mxConstants.STYLE_LABEL_POSITION, mxConstants.ALIGN_RIGHT, [edge] )  // how is the label position horizontally aligned
		graph.setCellStyles(mxConstants.STYLE_VERTICAL_LABEL_POSITION, mxConstants.ALIGN_TOP, [edge] ) 
		
		// properties for change
		graph.setCellStyles(mxConstants.STYLE_EDITABLE, 0, [edge] )     // you cant edit the text of the link
		graph.setCellStyles(mxConstants.STYLE_MOVABLE, 0, [edge] )      // you cant move the edge
		graph.setCellStyles(mxConstants.STYLE_RESIZABLE, 0, [edge] )    // you cant resize the edge
			
	}
	finally
	{
	     // Update the display
	     graph.getModel().endUpdate();
	}

	return edge;
}

//
//  Utility Functions
//
function getDM3KBlockLocationSize(block) {
    return [block.geometry.x, block.geometry.y, block.geometry.width, block.geometry.height]

}

function getDM3KBlockType(block) {
	// we assume that type is always the name of the first child vertex in the block
	let typeLabel = block.getChildAt(0);
	
	// we assume that the type name is the value of the child
	return typeLabel.getValue();
}
