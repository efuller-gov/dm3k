<template>
  <div>
    <img id="dm3k-logo" src="../assets/dm3k_logo_expanded.svg">
    <div id="graphContainer">
    </div>
  </div>
</template>

<script>
  import {Dm3kGraph} from '../js/dm3kgraph/dm3kGraph';

  export default {
    name: 'GraphRenderer',
    data() {
      return {
        infoIcon: require('../assets/info-icon.png'),
        solnExplainer: require("../assets/output-explainer.png")
      }
    },
    mounted() {
        this.loadDm3kGraph();
        this.addListener();
        this.$root.$on('zoom-in', this.zoomIn)
        this.$root.$on('zoom-out', this.zoomOut)
        this.$root.$on('clear-graph', this.clearGraph)
    },
    watch: {
        '$store.state.resources': {
            deep: true,
            handler(resources) {
                for (let latest of resources.filter(x=>x.drawn==false)){
                  let newResType = latest.resType
                  let newResName = latest.resName
                  let newBudgetNameList = latest.newBudgetNameList
                  this.$store.state.dm3kGraph.addCompleteResource(newResType, newResName, newBudgetNameList)
                  latest.drawn = true
                }
            }
        },
         '$store.state.activities': {
            deep: true,
            handler(activities) {
                for (let latest of activities.filter(x=>x.drawn==false)){
                  let newActType = latest.newActType
                  let newActName = latest.actName
                  let existingResName = latest.existingResName
                  let newRewardName = latest.newRewardName
                  let costNum = 0 //REMOVE hardcoded workaround here??
                  this.$store.state.dm3kGraph.addCompleteActivity(newActType, newActName, existingResName, newRewardName, costNum)
                  latest.drawn = true
                }
            }
        },
        '$store.state.allocatedLinks': {
            deep: true,
            handler(links) {
                let latest = links[links.length-1]
                let actName = latest.actName
                let existingResName = latest.existingResName
                let newRewardName = latest.newRewardName
                this.$store.state.dm3kGraph.addAllocation(actName, existingResName, newRewardName)
            }
        },
        '$store.state.containsLinks': {
            deep: true,
            handler(links) {
                for (let latest of links.filter(x=>x.drawn==false)){
                  this.$store.state.dm3kGraph.addContains(latest.resName, latest.ccName);
                  latest.drawn = true
                }
            }
        }
    },
    methods: {
        loadDm3kGraph() {
          this.$store.state.dm3kGraph = new Dm3kGraph(document.querySelector('#graphContainer'))
        },
        zoomIn(){
           this.$store.state.dm3kGraph.graph.zoomIn()
        },
        zoomOut(){
          this.$store.state.dm3kGraph.graph.zoomOut()
        },
        addListener(){
          let container = document.getElementById('graphContainer')
          container.addEventListener('CircleIClicked', this.emitModal)
          container.addEventListener('xIconClicked', this.deleteResAct)
        },
        emitModal(e){
          this.$root.$emit('show-instance-modal', e)
        },
        deleteResAct(e){
          this.$root.$emit('delete-res-act', e)
          
          if (e.detail.type == 'Resource'){
            this.$store.state.dm3kGraph.removeResource(e.detail.name, e.detail.budget[0])
          }
          if (e.detail.type == 'Activity'){
            this.$store.state.dm3kGraph.removeActivity(e.detail.name, e.detail.cost,  e.detail.reward)
          }
        },
        clearGraph(){
          this.$store.state.dm3kGraph.clearAll()
        },
    }
  };
</script>

<style scoped>
  #dm3k-logo{
    position: absolute;
    height: 8%;
    margin-left: 1%;
    margin-top: 1%;
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
