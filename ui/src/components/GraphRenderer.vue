<template>
  <div>
    <img id="dm3k-logo" src="../assets/dm3k_logo.svg">
    <div id="graphContainer">
    </div>
  </div>
</template>

<script>
  import $ from 'jquery'
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
                // let latest = resources[resources.length-1]
                console.log("resources ", resources)
                // if (resources == []){
                //   this.clearGraph()
                // }
                // console.log("resources.filter(x=>x.drawn==false) ", resources.filter(x=>x.drawn==false))
                for (let latest of resources.filter(x=>x.drawn==false)){
                  let newResType = latest.resType
                  let newResName = latest.resName
                  let newBudgetNameList = latest.newBudgetNameList
                  // console.log(">> graphRenderer: render ", newResName)
                  // console.log("this.dm3kGraph ", this.dm3kGraph)
                  // console.log("res length ", this.dm3kGraph.resources.length)
                  // console.log(latest)
                  this.dm3kGraph.addCompleteResource(newResType, newResName, newBudgetNameList)
                  latest.drawn = true
                }
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
        addListener(){
          let container = document.getElementById('graphContainer')
          container.addEventListener('CircleIClicked', this.emitModal)
        },
        emitModal(e){
          this.$root.$emit('show-instance-modal', e)
        },
        clearGraph(){
          console.log(">>>>> Clearing graph render")
          $('#graphContainer').empty()
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
