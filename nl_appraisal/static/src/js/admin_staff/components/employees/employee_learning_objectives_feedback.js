ELearningObjectivesFeedback = {
    inject: ['appraisalData', 'submitFunction', 'changeComponent', 'toggleChat'],
    data() {
        return {
            formData: {},
            disableButton: false,
            buttonText: "Save and next",
            readOnlyMode: true,
            editButtonText: "Edit"
        }
    },
    watch: {
      appraisalData: {
        handler(newVal, oldVal) {
          if (newVal.value) this.writeDataToForm(newVal);
        },
        immediate: true,
        deep: true,
      },
    },
    methods: {
        changeReadOnlyMode(changeData=true) {
            this.readOnlyMode = !this.readOnlyMode
            if (this.readOnlyMode) {
                this.editButtonText = "Edit"
                this.toggleChat('block')
                if (changeData) this.writeDataToForm(this.appraisalData)
            }else {
                this.editButtonText = "Discard"
                this.toggleChat('none')
            }
        },
        writeDataToForm(data) {
            this.formData['appraisal_id'] = data.value['id']
            this.formData['has_emp_objective'] = true
            this.formData['emp_individual_objectives_feedback'] = {}
            if (data.value['individual_objectives']) {
                data.value['individual_objectives'].forEach((obj, index) => {
                    this.formData.emp_individual_objectives_feedback['objective_'+ index] = {name: obj.name, id: obj.id, emp_feedback: obj.employee_feedback }
                });
            }
        },
        async submitForm() {
            this.disableButton = true
            this.buttonText = "Saving..."
            result = await this.submitFunction(this.formData)
            if (result) {
                this.changeReadOnlyMode(changeData=false)
                if (this.appraisalData.value.metaInfo.learning_objective_feed_state){
                    this.changeComponent('ESelfAssessment')
                }
            }
            this.disableButton = false
            this.buttonText = "Save and next"
        }
      },
  template: `
        <div>
        <h4 style="font-size: 20px;background: #ffffff;padding: 10px 0;margin-top: 20px;border-bottom: 4px solid #875a7b;text-transform: uppercase;">Learning Objectives Feedback </h4>
        <div class="text-center">
        <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" data-name="Layer 1" width="200" height="200" viewBox="0 0 843.57946 640.51678"><path d="M602.65363,129.74161H226.33527a48.17928,48.17928,0,0,0-48.125,48.12512V619.74252a48.17923,48.17923,0,0,0,48.125,48.12506H602.65363a48.17923,48.17923,0,0,0,48.125-48.12506V177.86673A48.17928,48.17928,0,0,0,602.65363,129.74161Z" transform="translate(-178.21027 -129.74161)" fill="#f2f2f2"/><path d="M602.65412,143.59579H226.33527a34.30948,34.30948,0,0,0-34.271,34.27094V619.74252a34.30946,34.30946,0,0,0,34.271,34.27088H602.65412a34.30937,34.30937,0,0,0,34.27051-34.27088V177.86673A34.30938,34.30938,0,0,0,602.65412,143.59579Z" transform="translate(-178.21027 -129.74161)" fill="#fff"/><path d="M546.01784,272.08142H355.71616a8.01411,8.01411,0,0,1,0-16.02822H546.01784a8.01411,8.01411,0,1,1,0,16.02822Z" transform="translate(-178.21027 -129.74161)" fill="#f2f2f2"/><path d="M579.07606,299.12906H355.71616a8.01412,8.01412,0,0,1,0-16.02823h223.3599a8.01412,8.01412,0,0,1,0,16.02823Z" transform="translate(-178.21027 -129.74161)" fill="#f2f2f2"/><path d="M546.01784,393.29489H355.71616a8.01411,8.01411,0,0,1,0-16.02822H546.01784a8.01411,8.01411,0,1,1,0,16.02822Z" transform="translate(-178.21027 -129.74161)" fill="#f2f2f2"/><path d="M579.07606,420.34253H355.71616a8.01412,8.01412,0,0,1,0-16.02823h223.3599a8.01412,8.01412,0,0,1,0,16.02823Z" transform="translate(-178.21027 -129.74161)" fill="#f2f2f2"/><path d="M546.01784,514.50836H355.71616a8.01411,8.01411,0,0,1,0-16.02823H546.01784a8.01412,8.01412,0,1,1,0,16.02823Z" transform="translate(-178.21027 -129.74161)" fill="#f2f2f2"/><path d="M579.07606,541.556H355.71616a8.01412,8.01412,0,0,1,0-16.02823h223.3599a8.01412,8.01412,0,0,1,0,16.02823Z" transform="translate(-178.21027 -129.74161)" fill="#f2f2f2"/><path d="M313.08745,311.40753H245.7415a3.847,3.847,0,0,1-3.84277-3.84277V247.61749a3.847,3.847,0,0,1,3.84277-3.84277h67.34595a3.847,3.847,0,0,1,3.84277,3.84277v59.94727A3.847,3.847,0,0,1,313.08745,311.40753Z" transform="translate(-178.21027 -129.74161)" fill="#e6e6e6"/><path d="M313.08745,432.621H245.7415a3.847,3.847,0,0,1-3.84277-3.84277V368.831a3.847,3.847,0,0,1,3.84277-3.84277h67.34595a3.847,3.847,0,0,1,3.84277,3.84277v59.94727A3.847,3.847,0,0,1,313.08745,432.621Z" transform="translate(-178.21027 -129.74161)" fill="#e6e6e6"/><path d="M313.08745,553.83447H245.7415a3.847,3.847,0,0,1-3.84277-3.84277V490.04443a3.847,3.847,0,0,1,3.84277-3.84277h67.34595a3.847,3.847,0,0,1,3.84277,3.84277V549.9917A3.847,3.847,0,0,1,313.08745,553.83447Z" transform="translate(-178.21027 -129.74161)" fill="#e6e6e6"/><path d="M934.16522,547.652l2.98548-26.10867,14.969-130.90768,2.98548-26.10867a48.17929,48.17929,0,0,0-42.34617-53.28082L573.09668,272.40642a48.17924,48.17924,0,0,0-53.28086,42.346l-.00771.06744L498.88352,497.81005l-.00771.06744a48.17923,48.17923,0,0,0,42.34611,53.2808L880.8843,589.99806A48.17929,48.17929,0,0,0,934.16522,547.652Z" transform="translate(-178.21027 -129.74161)" fill="#e6e6e6"/><path d="M920.40067,546.07857l3.5361-30.924,13.86792-121.278,3.536-30.92349a34.30948,34.30948,0,0,0-30.1556-37.94256L571.52276,286.17073a34.30948,34.30948,0,0,0-37.94245,30.15568l-.00771.06743L512.648,499.384l-.00776.06792A34.30934,34.30934,0,0,0,542.79584,537.394l339.66238,38.83977A34.30936,34.30936,0,0,0,920.40067,546.07857Z" transform="translate(-178.21027 -129.74161)" fill="#fff"/><path d="M864.80353,380.15794l-189.0696-21.61976a8.01412,8.01412,0,1,1,1.82093-15.92446l189.0696,21.61976a8.01412,8.01412,0,0,1-1.82093,15.92446Z" transform="translate(-178.21027 -129.74161)" fill="#e6e6e6"/><path d="M894.5749,410.78613,672.6611,385.4107a8.01412,8.01412,0,1,1,1.82094-15.92446l221.91379,25.37544a8.01411,8.01411,0,0,1-1.82093,15.92445Z" transform="translate(-178.21027 -129.74161)" fill="#e6e6e6"/><path d="M888.38764,464.38258,561.218,426.97133a8.01412,8.01412,0,0,1,1.82093-15.92446l327.16968,37.41125a8.01412,8.01412,0,1,1-1.82094,15.92446Z" transform="translate(-178.21027 -129.74161)" fill="#e6e6e6"/><path d="M886.36619,491.37532l-328.221-37.53147a8.01412,8.01412,0,0,1,1.82093-15.92446l328.221,37.53147a8.01412,8.01412,0,0,1-1.82093,15.92446Z" transform="translate(-178.21027 -129.74161)" fill="#e6e6e6"/><path d="M882.36643,517.03944,555.19676,479.62819a8.01412,8.01412,0,1,1,1.82093-15.92446L884.18736,501.115a8.01412,8.01412,0,0,1-1.82093,15.92446Z" transform="translate(-178.21027 -129.74161)" fill="#e6e6e6"/><path d="M880.345,544.03218l-328.221-37.53147a8.01412,8.01412,0,0,1,1.82093-15.92446l328.221,37.53147a8.01412,8.01412,0,1,1-1.82093,15.92446Z" transform="translate(-178.21027 -129.74161)" fill="#e6e6e6"/><path d="M628.91345,392.76672l-66.90992-7.651a3.847,3.847,0,0,1-3.38133-4.25447l6.81048-59.55914a3.847,3.847,0,0,1,4.25446-3.38133l66.90993,7.651a3.847,3.847,0,0,1,3.38132,4.25446l-6.81047,59.55915A3.847,3.847,0,0,1,628.91345,392.76672Z" transform="translate(-178.21027 -129.74161)" fill="#875a7b"/><path d="M1020.78973,770.09988h-219a1,1,0,0,1,0-2h219a1,1,0,0,1,0,2Z" transform="translate(-178.21027 -129.74161)" fill="#3f3d56"/><path d="M938.55609,388.06207a9.37695,9.37695,0,0,0,8.41945,11.6556l6.77492,20.32879,13.35789-1.10405-9.9707-28.5738a9.42779,9.42779,0,0,0-18.58156-2.30654Z" transform="translate(-178.21027 -129.74161)" fill="#ffb8b8"/><path d="M948.78649,521.187l0,0a12.08366,12.08366,0,0,0,19.9793-6.32315l10.57975-48.473a47.876,47.876,0,0,0-1.23439-24.98L965.7291,403.23538a4,4,0,0,0-5.59557-2.34269l-8.08121,4.04582a4,4,0,0,0-2.05021,4.69365l.81477,2.802a134.70325,134.70325,0,0,1,1.02888,71.4844l-6.58107,25.33A12.08364,12.08364,0,0,0,948.78649,521.187Z" transform="translate(-178.21027 -129.74161)" fill="#875a7b"/><polygon points="728.243 629.901 716.811 629.9 711.374 585.804 728.247 585.805 728.243 629.901" fill="#ffb8b8"/><path d="M708.64439,626.63322H730.6922a0,0,0,0,1,0,0v13.88195a0,0,0,0,1,0,0H694.76246a0,0,0,0,1,0,0v0A13.88193,13.88193,0,0,1,708.64439,626.63322Z" fill="#2f2e41"/><polygon points="789.864 629.901 778.432 629.9 772.995 585.804 789.868 585.805 789.864 629.901" fill="#ffb8b8"/><path d="M770.26564,626.63322h22.04781a0,0,0,0,1,0,0v13.88195a0,0,0,0,1,0,0H756.38371a0,0,0,0,1,0,0v0A13.88193,13.88193,0,0,1,770.26564,626.63322Z" fill="#2f2e41"/><circle cx="756.38308" cy="291.8647" r="24.56103" fill="#ffb8b8"/><path d="M850.61084,581.78436a9.377,9.377,0,0,1,12.09228-7.77927l13.72625-16.45445,12.03377,5.90259-19.71048,22.96462a9.42779,9.42779,0,0,1-18.14182-4.63349Z" transform="translate(-178.21027 -129.74161)" fill="#ffb8b8"/><path d="M940.57354,446.16634a26.205,26.205,0,1,0-4.91018-51.82531c-5.40118-3.27952-11.6809-5.48627-17.97478-4.925s-12.51835,4.29788-14.87192,10.16207.17487,13.59411,6.02708,15.97731c3.75184,1.52786,7.98866.78692,11.99255.1708s8.37171-1.01817,11.85634,1.04774,5.05107,7.60548,1.93026,10.18835a10.73847,10.73847,0,0,0-3.0842,11.82027C933.10715,442.83887,937.38805,446.09752,940.57354,446.16634Z" transform="translate(-178.21027 -129.74161)" fill="#2f2e41"/><path d="M971.04643,580.81327l4.35678,165.33964a4,4,0,0,1-4.20243,4.10017l-14.35213-.73225a4,4,0,0,1-3.74658-3.36683L936.031,638.76494a2,2,0,0,0-3.92705-.12222l-23.10758,103.3966a4,4,0,0,1-5.24374,2.89644l-14.24374-.87a4,4,0,0,1-2.64986-4.05306l12.434-160.76415Z" transform="translate(-178.21027 -129.74161)" fill="#2f2e41"/><path d="M978.03835,502.28255c2.403-25.05537-16.01923-47.71792-41.12634-49.5007-10.81772-.76813-27.61219-1.04273-33.14841,13.13648-16.6774,42.71375,12.51774,41.67582,2.45884,78.68292s-18.94294,39.128-5.14121,41.80029,75.86671,18.447,73.31817-7.60005C972.83287,562.79095,975.64139,527.27536,978.03835,502.28255Z" transform="translate(-178.21027 -129.74161)" fill="#875a7b"/><path d="M908.71686,461.57372l0,0a12.08366,12.08366,0,0,1,16.29393,13.1781l-7.8391,48.991a47.876,47.876,0,0,1-10.26518,22.80677L881.44705,577.5737a4,4,0,0,1-6.06458.13914L869.335,570.997a4,4,0,0,1-.196-5.11813l1.78109-2.31142a134.7031,134.7031,0,0,0,27.04467-66.179l3.11643-25.98473A12.08366,12.08366,0,0,1,908.71686,461.57372Z" transform="translate(-178.21027 -129.74161)" fill="#875a7b"/></svg>
      </div>
        <legend class="mb-3 page-hint"><p class="hint">
        This section outlines the Learning and Development initiatives and objectives (formal trainings, projects, assignments, etc.) that were set to you by your supervisor.  Please provide your feedback/input with regards to each learning/development objective below.</p></legend>
            <div>
                <form class="form-group" @submit.prevent="submitForm">
                    <div class="form_buttons" v-if="appraisalData.value.metaInfo.hasCurrentComponentAccess">
                        <button type="button" class="btn btn-secondary text-white" @click="changeReadOnlyMode" v-if="!disableButton">{{ editButtonText }}</button>
                        <button  class="btn btn-secondary text-white" :disabled="disableButton" v-if="!readOnlyMode">{{ buttonText }}</button>
                    </div>
                    <fieldset class="mt-5">
                        <template v-for="(objective, key, index) in formData.emp_individual_objectives_feedback" :key="index">
                        <h6 class="objective-title mt-2">Learning Objective <label for="" class="font-weight-normal">{{index+1}}: </label></h6>
                        <p class="objective-learning-body mt-3 mb-3">
                        
                        {{ objective.name }}
                        </p>
                        <h6 class="objective-title mt-2">Employee Feedback</h6>
                            <textarea class="form-control mt-3 mb-3 disabled-textarea" rows="5" placeholder="Provide your comments regarding this objective here ..." :disabled="readOnlyMode"
                                v-model="formData.emp_individual_objectives_feedback['objective_'+index].emp_feedback"></textarea>
                        </template>
                    </fieldset>
                </form>
            </div>    
        </div>
    `,
};