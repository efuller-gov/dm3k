<template>
  <div>
    <img id="dm3k-logo" src="../assets/dm3k_logo.svg">
    <div id="graphContainer">
      <div class="modal">
        <span class="close-btn" onclick="closeModal()">&times;</span>
        <div class="modal-header">
        </div>
        <div class="modal-content">
          <div id="table-left-aligned-content">
            <div id="table-title"></div>
          </div>
          <div id="table-and-control-buttons-container">
          <div id="instance-table-control-buttons">
            <button id="add-row">Add instance row</button>
          </div>
            <div id="modal-instance-table" class="instance-table"></div>
					</div>
        </div>
        <div class="modal-footer">
        </div>
			</div>
			<div id="soln-modal" class="soln-modal">
				<span class="close-btn" onclick="closeSolnModal()">&times;</span>
				<div class="modal-content">
					<img id='soln-explainer-graphic' onclick="location.href='./'" src="../assets/output-explainer.png">
					<p id="soln-title">Optimal Allocation Plan</p>
					<button id="soln-explainer-btn" onclick="toggleSolnGraphicExplainer()">Show me how to read this</button>
					<div id="soln-table-top-aligned-content">
						Size and sort activity instance columns by
						<select class="chosen-select" id="widthFunctionToggle">
							<option value="cost">cost</option>
							<option value="ratio">reward / cost ratio</option>
							<option value="reward">reward</option>
						</select>
					</div>
					<div id="soln-visualization"></div>
				</div>
				<div class="modal-footer">
				</div>
      </div>
    </div>
  </div>
</template>

<script>

  import {Dm3kGraph} from '../js/dm3kgraph/dm3kGraph';

  export default {
    name: 'GraphRenderer',
    data() {
      return {
        dm3kGraph: {},
        infoIcon: require('../assets/info-icon.png'),
        solnExplainer: require("../assets/output-explainer.png")
      }
    },
    mounted() {
        this.loadDm3kGraph();
        this.addListener();
    },
    watch: {
        '$store.state.resources': {
            deep: true,
            handler(resources) {
                let latest = resources[resources.length-1]
                let newResType = latest.resType
                let newResName = latest.resName
                let newBudgetNameList = latest.newBudgetNameList
                this.dm3kGraph.addCompleteResource(newResType, newResName, newBudgetNameList)
            }
        },
         '$store.state.activities': {
            deep: true,
            handler(activities) {
                let latest = activities[activities.length-1]
                let newActType = latest.newActType
                let newActName = latest.actName
                let existingResName = latest.existingResName
                let newRewardName = latest.newRewardName
                let costNum = 1 //REMOVE hardcoded workaround here??
                this.dm3kGraph.addCompleteActivity(newActType, newActName, existingResName, newRewardName, costNum)
            }
        },
        '$store.state.allocatedLinks': {
            deep: true,
            handler(links) {
                let latest = links[links.length-1]
                let actName = latest.actName
                let existingResName = latest.existingResName
                let newRewardName = latest.newRewardName
                this.dm3kGraph.addAllocation(actName, existingResName, newRewardName)
            }
        }

    },
    methods: {
        loadDm3kGraph() {
            this.dm3kGraph = new Dm3kGraph(document.querySelector('#graphContainer'))
        },
        showInstanceModal(){
          console.log("!!!! SHOW MODAL")
        },
        addListener(){
          let container = document.getElementById('graphContainer')
          container.addEventListener('CircleIClicked', this.showInstanceModal)
        }
    }
  };
</script>

<style scoped>
  #dm3k-logo{
    position: absolute;
  }
  .container {
    border-style: groove;
    border-width: thin;
    border-radius: 5px;
    height: 100%;
    width: 100%;
    padding: 5px;
    max-height: 72vh;
    max-width: 100%;
    overflow: hidden;
    border-color: grey;
    margin: 0px;
    transition: border-color 0.2s ease-in-out;
  }

  .container:hover {
    border-color: #242424;
  }

  #graphContainer {
    width: 100%;
    /* height: 100%; */
    margin: 0px;
    padding: 0px;
    min-height: 72vh;
    overflow: hidden;
  }

  .float-tool-bar {
    position: relative;
    top: 0px;
    bottom: 0px;
    right: 0px;
    left: 0px;
    width: 40px;
    height: 200px;
    padding: 0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .tool-btn {
    width: 40px;
    height: 40px;
    border-radius: 999px;
    background: #f5f5f5;
    box-shadow: 0 2px 8px 0 #dcdcdc;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    margin-bottom: 5px;
    pointer-events: auto;
  }

  .menu-btn {
    background: transparent;
    transition: 0ms;
  }

  .overlapContainer {
    position: relative;
    width: 100%;
  }

  .buttonList {
    pointer-events: none;
    padding: 5px 0px 0px 5px;
    list-style-type: none;
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0px;
    bottom: 0px;
    right: 0px;
    left: 0px;
    z-index: 1
  }

  li {
    pointer-events: none;
  }

  .textinfo {
    position: absolute;
    color: #b3b3b3;
    font-size: 14px;
    padding: 10px;
    bottom: 0px;
  }

</style>
