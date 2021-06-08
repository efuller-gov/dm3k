import mxgraph from './index';
import _ from 'lodash';

const {
  mxGraph,
  mxEvent,
  mxCellOverlay,
  mxImage,
  mxConstants,
  mxUtils,
  mxRectangle
} = mxgraph;

const boxHeight = 25;
const boxWidth = 70;
const boxSpace = 5;
const tacticStyle = 'fontStyle=1;fontColor=white;fontSize=9;fillColor=#607d8b;strokeColor=grey;whiteSpace=wrap;';
const techniqueStyle = 'fontStyle=0;fontColor=#404040;fontSize=8;fillColor=white;strokeColor=grey;whiteSpace=wrap;';

export class AttackGraph {

  /**
      *  Make a attackGraph
      *
      *  @param (div) container: the div that acts as the container for all graph objects
      */
  constructor(container, attackTactics, attackTechniques) {
    // Disables the built-in context menu
    mxEvent.disableContextMenu(container);

    // change the selection style
    mxConstants.VERTEX_SELECTION_COLOR = 'black';
    mxConstants.VERTEX_SELECTION_STROKEWIDTH = 3;
    mxConstants.VERTEX_SELECTION_DASHED = false;
    mxConstants.HANDLE_SIZE = 0; // makes resize boxes disappear

    // Creates the graph inside the given container
    this.graph = new mxGraph(container);
    const initialHeight = document.getElementById('graphContainer').offsetHeight;
    const initialWidth = document.getElementById('graphContainer').offsetWidth;
    this.graph.minimumContainerSize = new mxRectangle(0, 0, initialWidth, initialHeight);

    // Do not allow removing labels from parents
    this.graph.graphHandler.removeCellsFromParent = false;

    // Disables basic selection and cell handling
    this.graph.setEnabled(false);

    // enables HTML labels as wrapping is only available for those
    this.graph.setHtmlLabels(true);
    this.graph.isLabelClipped = _.constant(true);

    // Do not allow editing
    this.graph.isCellEditable = _.constant(false);

    // allow for custom attributes
    this.graph.convertValueToString = function(cell) {
      if (mxUtils.isNode(cell.value)) {
        return cell.getAttribute('label', '');
      }
    };

    // do not allow moving
    this.graph.isCellMovable = _.constant(false);

    // set up panning
    this.graph.setPanning(true);
    this.graph.panningHandler.useLeftButtonForPanning = true;

    // zooms so that graph top left stays in top left of window
    this.graph.centerZoom = false;

    // install a handler for click events in the graph
    var boundClickFunction = function(sender, evt) {
      var box = evt.getProperty('cell');

      if (box != null) {

        var event = null;
        var idList = [];
        if (this.isBoxTechnique(box)) {
          idList.push({
            id: box.getAttribute('Tnum', ''),
            name: box.getAttribute('label', ''),
            label: 'ATT&CK Technique: ' + box.getAttribute('label', ''),
            type: 'att&ck.technique'
          });
        } else {
          idList.push({
            id: box.getAttribute('Tnum', ''),
            name: box.getAttribute('label', ''),
            label: 'ATT&CK Tactic: ' + box.getAttribute('label', ''),
            type: 'att&ck.tactic'
          });
        }

        if (this.graph.isCellSelected(box)) {
          this.graph.removeSelectionCell(box);

          // make an event from the container so that other components can react to removal
          event = new CustomEvent(
            'newBoxesDeselected',
            {
              detail: {
                boxesDeselected: idList
              },
              bubbles: true,
              cancelable: true
            }
          );
        } else {
          this.graph.addSelectionCell(box);

          // make an event from the container so that other components can react to removal
          event = new CustomEvent(
            'newBoxesSelected',
            {
              detail: {
                boxesSelected: idList
              },
              bubbles: true,
              cancelable: true
            }
          );
        }
        container.dispatchEvent(event);
      }
    }.bind(this);
    this.graph.addListener(mxEvent.CLICK, boundClickFunction);

    // capture the att&ck information
    this.attackTactics = attackTactics;
    this.attackTechniques = attackTechniques;
    this.tacticOrder = [
      'initial-access',
      'execution',
      'persistence',
      'privilege-escalation',
      'defense-evasion',
      'credential-access',
      'discovery',
      'lateral-movement',
      'collection',
      'command-and-control',
      'exfiltration',
      'impact'
    ];

    this.techniqueMap = {};
    this.renderATTACKGraph();
  }

  isBoxTechnique(box) {
    var boxType = box.getAttribute('type', '');
    return (boxType === 'technique');
  }

  renderATTACKGraph() {
    var xStart = boxSpace;
    var yStart = boxSpace;

    // set rendering to false, this is for fit later
    this.graph.view.rendering = false;

    // for each tactic, place the technique boxes below it
    for (var tactic of this.tacticOrder) {
      yStart = boxSpace;
      var tacticObj = _.find(this.attackTactics, {id: tactic});
      var tdoc = mxUtils.createXmlDocument();
      var tnode = tdoc.createElement(tacticObj.id);
      tnode.setAttribute('label', tacticObj.name);
      tnode.setAttribute('Tnum', tacticObj.id);
      tnode.setAttribute('type', 'tactic');
      this.placeBox(tacticObj.id, tnode, xStart, yStart, tacticStyle);

      for (var technique of this.getTechniquesFromTactic(tacticObj)) {
        yStart = yStart + boxHeight + boxSpace;
        var doc = mxUtils.createXmlDocument();
        var node = doc.createElement(tacticObj.id + '_' + technique.id);
        node.setAttribute('label', technique.name);
        node.setAttribute('Tnum', technique.id);
        node.setAttribute('type', 'technique');
        var id = tacticObj.id + '_' + technique.id; // should be unique to techniques that appear in multiple tactics
        this.placeBox(id,
          node,
          xStart,
          yStart,
          techniqueStyle);

        var box = this.graph.getModel().getCell(id);

        // update the technique Map so we can use this to select boxes
        if (technique.id in this.techniqueMap) {
          this.techniqueMap[technique.id].push(box);
        } else {
          this.techniqueMap[technique.id] = [];
          this.techniqueMap[technique.id].push(box);
        }

      }

      xStart = xStart + boxWidth + boxSpace;

      // update the technique Map
      var tbox = this.graph.getModel().getCell(tacticObj.id);
      this.techniqueMap[tacticObj.id] = [];
      this.techniqueMap[tacticObj.id].push(tbox);

    }

    // fit the graph
    this.fitWidth();

  }

  fitAll() {
    // fit the graph
    // border=mxgraph.border, keepOrigin=false, margin=0, enabled=true, ignoreWidth=false, ignoreHeight=false, maxHeight
    //   - setting ignoreHeight to false, makes it zoom to the tactics
    this.graph.fit(this.graph.border, false, 0, true, false, false);
    this.graph.view.rendering = true;
    this.graph.refresh();

    var margin = 2;
    var max = 3;

    var bounds = this.graph.getGraphBounds();
    var cw = this.graph.container.clientWidth - margin;
    var ch = this.graph.container.clientHeight - margin;
    var w = bounds.width / this.graph.view.scale;
    var h = bounds.height / this.graph.view.scale;
    var s = Math.min(max, Math.min(cw / w, ch / h));

    this.graph.view.scaleAndTranslate(s,
      (margin + cw - w * s) / (2 * s) - bounds.x / this.graph.view.scale,
      (margin + ch - h * s) / (2 * s) - bounds.y / this.graph.view.scale);
  }

  fitWidth() {
    // fit the graph
    // border=mxgraph.border, keepOrigin=false, margin=0, enabled=true, ignoreWidth=false, ignoreHeight=false, maxHeight
    //   - setting ignoreHeight to false, makes it zoom to the tactics
    //   - setting the margin to 30 gives room on both sides of the tactics
    this.graph.fit(this.graph.border, false, 200, true, false, true);
    this.graph.view.rendering = true;
    this.graph.refresh();
    this.graph.view.scaleAndTranslate(this.graph.view.scale, 105 / this.graph.view.scale, 0);

  }

  placeBox(name, text, xLoc, yLoc, style) {
    var parent = this.graph.getDefaultParent();
    this.graph.getModel().beginUpdate();
    try {
      // call structure is parent, id, value,x,y,width,heigh,style
      // so id=name and name is set above in RenderAttackGraph as a techniques id
      this.graph.insertVertex(parent, name, text, xLoc, yLoc, boxWidth, boxHeight, style);

    } finally {
      // Update the display
      this.graph.getModel().endUpdate();
    }

  }

  setTechniqueIndicators(listOfTechExtIds) {
    // add overlay to each id in list
    var check = new mxCellOverlay(new mxImage('assets/images/sigma_logo.png', 15, 15));
    var pt = check.offset;
    pt.x = -5;
    pt.y = -5;

    this.graph.getModel().beginUpdate();
    try {
      for (var extId of listOfTechExtIds) {
        var boxlist = this.techniqueMap[extId];
        if (_.isArray(boxlist)) {
          for (var box of boxlist) {
            // remove the previous overlays attached to this box
            this.graph.clearCellOverlays(box);
            this.graph.addCellOverlay(box, check);
          }
        }
      }

    } finally {
      // Update the display
      this.graph.getModel().endUpdate();
    }
  }

  getSelectedTechniques() {
    var allSelected = this.graph.getSelectionCells();
    var idList = [];
    for (var sbox of allSelected) {
      // push out objects with id and name
      idList.push({
        id: sbox.getAttribute('Tnum', ''),
        name: sbox.getAttribute('label', '')
      });
    }
    return idList;
  }

  setSelectedTechniques(techniqueArray) {
    this.graph.clearSelection();
    for (var extId of techniqueArray) {
      var boxlist = this.techniqueMap[extId.id];
      for (var cell of boxlist) {

        if (this.isBoxTechnique(cell)) {
          this.graph.addSelectionCell(cell);
        } else {
          this.graph.addSelectionCell(cell);
          for (var info of this.getTechniquesFromTactic(extId)) {
            var subCellList = this.techniqueMap[info.id];
            for (var subCell of subCellList) {
              this.graph.addSelectionCell(subCell);
            }

          }
        }
      }
    }
  }

  getTechniquesFromTactic(tactic) {
    return _.filter(this.attackTechniques, function(technique) {
      return _.includes(technique.tactics, tactic.id);
    });
  }

  clearTechniqueIndicators(listOfTechExtIds) {
    this.graph.getModel().beginUpdate();
    try {
      for (var extId of listOfTechExtIds) {
        var boxlist = this.techniqueMap[extId];
        for (var box of boxlist) {
          // remove the previous overlays attached to this box
          this.graph.clearCellOverlays(box);
        }
      }
    } finally {
      // Update the display
      this.graph.getModel().endUpdate();
    }
  }

  setGraphMinimumContainerSize(height, width) {
    this.graph.minimumContainerSize = new mxRectangle(0, 0, width, height);
  }
}
