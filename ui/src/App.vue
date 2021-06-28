<template>
  <div id="app">
    <GraphRenderer 
     @clear-graph="clearGraph"
    />
    <Modals />
    <WorksheetPane 
      @add-resource="addResource" 
      @add-existing-allocation="addAllocation"  
      @add-new-allocation="addActivity"
      @clear-graph="clearGraph"
      @zoom-in="addActivity"
      @zoom-out="clearGraph"
    />
  </div>
</template>

<script>
import WorksheetPane from './components/WorksheetPane.vue'
import GraphRenderer from './components/GraphRenderer.vue'
import Modals from './components/Modals.vue'
import $ from 'jquery'

export default {
  name: 'App',
  components: {
    GraphRenderer,
    Modals,
    WorksheetPane,
  },
  methods: {
      addResource(resourceObj){
        this.$store.commit('addResource', resourceObj)
      },
      addAllocation(activityObj){
        this.$store.commit('addAllocation', activityObj)
      },
      addActivity(activityObj){
        this.$store.commit('addActivity', activityObj)
      },
      clearGraph(){
        this.$store.commit('clearGraph')
        $('#graphContainer').empty()
        // const customEvent = new CustomEvent('clear-graph-render');
        // document.dispatchEvent(customEvent);
      }
  }
}
</script>

<style>
  #app {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    margin: 0px;
    background-image: url("./assets/grid-dashed.png");
    background-size:  100%;
    font-family: 'Roboto', sans-serif;
    font-size: 14px;
    color: #707070;
    margin-bottom: 0px;
    height: 100vh;
  }
  :root {
    --top-padding-for-worksheets: 15px;
  }
  body {
    margin: 0px;
    background-image: url("./assets/grid-dashed.png");
    background-size:  100%;
    font-family: 'Roboto', sans-serif;
    font-size: 14px;
    color: #707070;
    margin-bottom: 0px;
  }
  
  .flow {
    animation: dash 0.5s linear;
    animation-iteration-count: infinite;
    stroke-dasharray: 8;
  }
  @keyframes dash {
    to {
      stroke-dashoffset: -16;
    }
  }
  #zoom-buttons{
    margin: 3%;
  }
  .zoom-button{
    height: 40px;
    width: 40px;
    font-size: 30px;
    line-height: 15px;
    margin-right: 10px;
    vertical-align: center;
    text-align: middle;
    color: #707070;
    background: white;
    border-radius: 5px;
    border-width: 0px;
    border-style: solid;
    border-color: lightgray;
    box-shadow:
    0 2.8px 2.2px   rgba(0.014, 0.014, 0.014, 0.014),
    0 6.7px 5.3px   rgba(0.014, 0.014, 0.014, 0.014),
    0 12.5px 10px   rgba(0.014, 0.014, 0.014, 0.014),
    0 22.3px 17.9px rgba(0.014, 0.014, 0.014, 0.014),
    0 41.8px 33.4px rgba(0.014, 0.014, 0.014, 0.014),
    0 100px 80px    rgba(0.014, 0.014, 0.014, 0.014)
  }
  .zoom-button:focus{
    outline: none;
  }
  .zoom-button:hover{
    background-color: rgba(255,255,255,0.5);
  }
  .ele_inline {
    display: inline-block;
    padding-right: 150px;
  }
  .arg_inline {
    display: inline-block;
    padding-right: 30px;
  }
  .form-control-inline {
    display: inline;
    text-align: center;
  }
  .plus-minus-button {
    width: 120px;
    display: inline-block;
    vertical-align: bottom;
    background: #f7f6f6;
  }
  .error_txt {
    background-color:red;
    text-align: center;
  }
  #menu{
    width: 100%;
    height: 40vh;
    background: #E9EDF2;
    position: absolute;
    margin: 0px;
    margin-left: 0px;
    margin-right: 0px;
    /*margin-top: 45vh;*/
    bottom: 0;
    margin-bottom: 0px;
    overflow: hidden;
  }
  #graphContainer{
    width: 100%;
    height: 60vh;
    position: absolute;
    margin: 0px;
    margin-left: 0px;
    margin-right: 0px;
    margin-top: 0px;
    /*margin-bottom: 55vh;*/
  }
  #top-container{
    display: inline-flex;
  }
  .left_column {
    float: left;
    width: 23%;
    max-width: 22%;
    min-width: 22%;
    width: auto;
    height: 100%;
    padding-top: var(--top-padding-for-worksheets);
    padding-left: 2%;
    padding-right: 2%;
    border-left-style: dashed;
    border-color: lightgray;
    border-width: 1px;
    font-size: 0.8vw;
  }
  persistent_left_column {
    float: left;
    width: 23%;
    /*width: auto;*/
    height: 100%;
    padding-top: var(--top-padding-for-worksheets);
    padding-left: 20px;
    padding-right: 20px;
    border-left-style: dashed;
    border-color: lightgray;
    border-width: 1px;
  }
  #add-row{
    background :#e2e2e2;
    width: auto;
    height: 10%;
    padding: 2%;
    border-radius: 5px;
    border-width: 0px;
    font-weight: bold;
    color: #707070;
  }
  #add-row:hover{
    background-color: #cccccc;
  }
  .done-button {
    background: white;
    width: auto;
    /*height: 10%;*/
    height: 30px;
    padding-left: 4%;
    padding-right: 4%;
    border-radius: 5px;
    border-width: 0px;
    float: left;
    margin-right: 10%;
    font-weight: bold;
    color: #707070;
    font-size: 0.8vw;
  }
  .done-button:hover{
    background-color: rgba(255,255,255,0.5);
  }
  .chosen-select{
    background: #E9EDF2;
    border-style: solid;
    border: none;
    border-bottom: solid;
    border-color: #8e8e8e;
    border-bottom-width: 1.5px;
    -webkit-appearance: none;
    -webkit-border-radius: 0px;
    background-image: linear-gradient(45deg, transparent 50%, gray 50%), linear-gradient(135deg, gray 50%, transparent 50%);
    background-position: calc(100% - 10px) calc(0.5em), calc(100% - 5px) calc(0.5em), calc(100% - 2.5em) 0.5em;
    background-size: 5px 5px, 5px 5px, 1px 1.5em;
    background-repeat: no-repeat;
    -moz-appearance: none;
    padding: 0.3rem;
    height: auto;
    min-width: 100px;
    width: auto;
    margin-right: 10px;
    margin-left: 10px;
    color: #707070;
  }
  .chosen-select:focus{
    outline: none;
  }
  .activity-select{
    min-width: 135px;
    color: #707070;
  }
  #activity-submenu-container{
    margin-top: 5px;
  }
  .title-text{
    font-weight: bold;
    /* font-size: 12px; */
    /* font-size: 14px; */
    font-size: 0.9vw !important;
  }
  .explanatory-text{
    /* font-size: 12px; */
    font-size: 0.75vw;
  }
  .responsive-column-text{
    font-size: 0.9vw;
  }
  #hide-worksheet-button{
    padding: 0.3rem;
    height: auto;
    min-height: 10px;
    min-width: 100px;
    width: auto;
    margin-right: 10px;
    margin-left: 10px;
    color: #707070;
    float: right;
    font-size: 12px;
    font-weight: bold;
  }
  .shrink{
    height: 7.5vh !important;
  }
  #helper-image{
    margin-top: 4%;
    margin-left: 2%;
    vertical-align: text-bottom;
    height: 4vw;
  }
  /* TO DO: Willl have to fix this */
  /* span.remove-button-class{
    background: url("../assets/x-icon.svg"); no-repeat top left;
    background-size: contain;
    cursor: pointer;
    display: inline-block;
    height: 10px;
    width: 10px;
  } */
  input[type=text]{
    border-style: solid;
    border: none;
    border-bottom: solid;
    border-color: #8e8e8e;
    border-bottom-width: 1.5px;
    height: auto;
    margin-left: 5px;
    height: 18px;
    width: auto;
    max-width: 80px;
    background: #E9EDF2;
    color: #707070;
  }
  input[type=text].long-input{
    border-style: solid;
    border: none;
    border-bottom: solid;
    border-color: #8e8e8e;
    border-bottom-width: 1.5px;
    height: auto;
    margin-left: 5px;
    height: 18px;
    width: auto;
    /* max-width: 150px; */
    min-width: 150px;
    background: #E9EDF2;
    color: #707070;
  }
  input:focus {
      outline: none;
  }
  #modal-button{
    float: left;
    position: fixed;
  }
  .modal {
    display: none;
    position: fixed;
    width: 70%;
    height: 55%;
    margin-left: 15%;
    color: #707070;;
    background-color: white;
    border-radius: 5px;
    filter: drop-shadow(6px 6px 10px lightgray)
  }
  .soln-modal{
    display: none;
    position: fixed;
    width: 90%;
    height: 90%;
    margin-left: 5%;
    color: #707070;;
    background-color: white;
    border-radius: 5px;
    filter: drop-shadow(6px 6px 10px lightgray);
    overflow: hidden;
  }
  #soln-visualization{
    float: left;
    width: 95%;
    margin-right: 0px;
  }
  #soln-title {
    font-size: 0.98vw;
    font-weight: bold;
    margin-top: 2vw;
  }
  #soln-explainer-btn{
    float: right;
    font-size: 0.7vw;
    height: auto;
    padding: 0.5vw;
    font-weight: bold;
    vertical-align: center;
    text-align: middle;
    color: #707070;
    border-radius: 5px;
    border-width: 1px;
    border-style: solid;
    border-color: lightgray;
    background-color: #eeeeee;
    line-height: 15px;
  }
  #soln-explainer-btn:focus{
    outline: none;
  }
  #soln-explainer-btn:hover{
    background-color: lightgray;
  }
  #soln-explainer-graphic{
    display: none;
    width: 90%;
    position: absolute;
  }
  .grid{
    height: 60%;
  }
  .modal-content {
    position: relative; 
    margin: auto; 
    width: 80%;  
    -webkit-animation-name: animatetop;
    -webkit-animation-duration: 0.4s;
    animation-name: animatetop;
    animation-duration: 0.4s
  }
  .close-btn {
    float: right; 
    color: black;
    padding-top: 10px;
    padding-right: 20px;
    font-size: 24px;  
    font-weight: bold;
  }
  .close-btn:hover {
    color: darkgray;
  }
  #table-left-aligned-content{
    font-size: 14px;
    margin-top: 8%;
    float: left;
    width: 25%;
  }
  #soln-table-top-aligned-content{
    font-size: 0.8vw;
    float: left;
    width: auto;
  }
  #table-top-aligned-content{
    font-size: 14px;
    margin-top: 8%;
    float: left;
    width: auto;
  }
  #table-title{
    margin-bottom: 4%;
  }
  #table-title p{
    font-size: 20px;
    font-weight: bold;
  }
  @-webkit-keyframes animatetop {
    from {top:-300px; opacity:0} 
    to {top:0; opacity:1}
  }
  @keyframes animatetop {
    from {top:-300px; opacity:0}
    to {top:0; opacity:1}
  }
  .instance-table{
    margin-top: 20px;
    height: auto !important;
  }
  #instance-table-control-buttons{
    margin-top: 50px;
  }
  #table-and-control-buttons-container{
    float: right;
    width: 70%;
  }
  #modal-instance-table .tabulator-header {
    background-color: white;
    color: #707070;
    font-size: 11px !important;
  }
  .tabulator{
    border: 0px !important;
  }
  .tabulator .tabulator-tableHolder{
    background: #EFEFEF;
    /* background: white; */
  }
  #modal-instance-table .tabulator-tableHolder .tabulator-table .tabulator-row{
    background-color: white;
    color: #707070;
    font-size: 12px;
  }
  #modal-instance-table .tabulator-header .tabulator-col,
  #modal-instance-table .tabulator-header .tabulator-col-row-handle {
      white-space: normal;
  }
  #explanatory-info-column{
    float: left;
    width: 23%;
    /* width: 20%; */
    /*width: auto;*/
    height: 100%;
    padding-top: var(--top-padding-for-worksheets);
    padding-left: 20px;
    /* padding-right: 20px; */
    padding-right: 0px;
    border-left-style: dashed;
    border-color: lightgray;
    border-width: 1px;
  }
  #helper-info-div{
    float: right;
    width: 28%;
    /* font-size: 14px; */
    /*width: auto;*/
    height: 100%;
    padding-top: var(--top-padding-for-worksheets);
    padding-left: 30px;
    padding-right: 30px;
    border-left-style: dashed;
    border-color: lightgray;
    border-width: 1px;
    font-size: 0.8vw;
  }
  .menu-button{
    height: 15%;
    width: 100%;
    text-align: left;
    vertical-align: middle;
    /* font-size: 14px; */
    font-size: 0.9vw;
    padding: 10px;
    padding-left: 20px;
    margin-top: 2%;
    margin-bottom: 2%;
    background-color: rgba(255,255,255,1);
    font-weight: bold;
    color: #707070;
    display: inline;
    padding-top: 10px;
    border-width: thin;
    border-color: black;
    border-top-style: solid;
    border-bottom-style: solid;
    border-left-style: none;
    border-right-style: none;
    border-top-style: none;
    border-bottom-style: none;
    -webkit-box-shadow: none;
    -moz-box-shadow: none;
    box-shadow: none;
  }
  .menu-button:focus{
    outline: 0;
  }
  .menu-button:hover{
    background-color: rgba(255,255,255,0.5);
  }
  .menu-button.enabled{
    background-color: rgba(255,255,255,1);
    border-width: thick;
    border-color: #707070;
    border-top-style: none;
    border-bottom-style: none;
    border-left-style: none;
    border-right-style: solid;
    border-width: 4px;
  }
  .sub-menu{
    height: 8%;
    width: auto;
    font-weight: normal;
    margin-top: 0;
    margin-bottom: 2%;
    margin-right: 1%;
    vertical-align: middle;
    padding: 0;
    padding-left: 2%;
    padding-right: 2%;
    border-radius: 5px;
    font-size: 11px;
  }
  .sub-menu.enabled{
    border-color: #707070;
    border-style: solid;
    border-width: 2px;
  }
  .arrow {
    border: solid #707070;
    border-width: 0 2px 2px 0;
    display: inline-block;
    padding: 3px;
    margin-left: 5px;
  }
  .down {
    transform: rotate(45deg);
    -webkit-transform: rotate(45deg);
  }
  #worksheet_menu_column{
    float: left;
    max-width: 15%;
    width: auto;
    height: 100%;
    padding-top: 10px;
    border-left-style: none;
    border-color: lightgray;
    border-width: 1px;
    box-shadow:
    0 2.8px 2.2px   rgba(0, 0, 0, 0.034),
    0 6.7px 5.3px   rgba(0, 0, 0, 0.034),
    0 12.5px 10px   rgba(0, 0, 0, 0.034),
    0 22.3px 17.9px rgba(0, 0, 0, 0.034),
    0 41.8px 33.4px rgba(0, 0, 0, 0.034),
    0 100px 80px    rgba(0, 0, 0, 0.034)
  ;
  }
  .disabled{
    pointer-events: none;
    opacity: 0.4 !important;
  }
  .hide{
    display: none;
  }
  div.tooltip {
    position: absolute;
    text-align: left;
    height: auto;
    width: auto;
    color: #707070;
    padding: 8px;
    font-size: 12px;
    background: #eeeeee;
    border: 1px;
    border-radius: 1px;
    border-style: solid;
    border-color: #707070;
    pointer-events: none;
  }
  #widthFunctionToggle{
    background: #eeeeee;
    border-style: solid;
    border: none;
    border-bottom: solid;
    border-color: #8e8e8e;
    border-bottom-width: 1.5px;
    -webkit-appearance: none;
    -webkit-border-radius: 0px;
    background-image: linear-gradient(45deg, transparent 50%, gray 50%), linear-gradient(135deg, gray 50%, transparent 50%);
    background-position: calc(100% - 10px) calc(0.5em), calc(100% - 5px) calc(0.5em), calc(100% - 2.5em) 0.5em;
    background-size: 5px 5px, 5px 5px, 1px 1.5em;
    background-repeat: no-repeat;
    -moz-appearance: none;
    padding: 0.3rem;
    height: auto;
    /* min-width: 150px; */
    min-width: 8vw;
    width: auto;
    color: #707070;
    font-size: 0.8vw;
  }
</style>
