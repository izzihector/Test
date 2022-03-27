MSetProbationObjective = {
    inject: ['appraisalData', 'submitFunction', 'showFlashMessage', 'changeComponent', 'toggleChat'],
    data() {
        return {
            formData: {},
            disableButton: false,
            buttonText: "Save and next",
            total_list_objectives_length: 0,
            readOnlyMode: true,
            editButtonText: "Edit"
        }
    },
    watch: {
        total_list_objectives_length: {
            handler(newVal, oldVal) {
                if (newVal > 3) {
                    this.total_list_objectives_length = 3
                    this.showFlashMessage(message="Max 3 General Objectives can be set.", type="error")
                }else {
                    lenObjectives = Object.keys(this.formData['set_objectives']).length
                    if (this.total_list_objectives_length > lenObjectives) {
                        this.formData.set_objectives['objective_'+ lenObjectives] = {name: '', id: null, expected_outcome: '' }
                    }
                }
            },
            immediate: false
        },
        appraisalData: {
            handler(newVal, oldVal) {
                if (newVal.value) this.writeDataToForm(newVal)
            },
            immediate: true,
            deep: true
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
            if (data.value.state == 'probation_period') {
                this.buttonText = 'Save'
            } else {
                this.buttonText = 'Save and next'
            }

            this.formData['set_objectives'] = {}
            this.formData['appraisal_id'] = data.value['id']
            this.formData['setting_objectives'] = true
            if (data.value['objectives']) {
                lenObjectives = Object.keys(data.value['objectives']).length
                if (lenObjectives > 0) {
                    data.value['objectives'].forEach((obj, index) => {
                        this.formData.set_objectives['objective_'+ index] = {name: obj.name, id: obj.id, expected_outcome: obj.expected_outcome}
                    });
                    this.total_list_objectives_length =  lenObjectives
                }
            }
        },
        async submitForm() {
            this.disableButton = true
            this.buttonText = "Saving..."
            result = await this.submitFunction(this.formData)
            if (result) {
                this.changeReadOnlyMode(changeData=false)
                if (this.appraisalData.value.metaInfo.setting_general_objective_state && this.appraisalData.value.state != 'probation_period'){
                    this.changeComponent('ProbationSubmitForm')
                }
            }
            this.disableButton = false
            if (this.appraisalData.value.state == 'probation_period') {
                this.buttonText = 'Save'
            } else {
                this.buttonText = 'Save and next'
            }
        },
    },
    template: `
    <div>
    <h3 style="font-size: 20px;background: #ffffff;padding: 10px 0;margin-top: 20px;border-bottom: 4px solid #875a7b;text-transform: uppercase;">Objectives during the probation period.</h3>
    <p class="page-hint">Objectives to be set with agreement between supervisor and employee. A total of 3 key objectives/goals to be evaluatlted at the end of the probation. Objectives should be based on the employee Job Description, and induction into SCA culture, policies and values.</p>
    <p class="page-hint">To proceed with adding objective, click on 'Edit' and then 'Add Line' to add one or more objectives with their outcomes. Once completed, you use the navigation bar on the left side of the screen to validate and submit.</p>
    <div class="py-3">
        <form class="form-group" @submit.prevent="submitForm">
            <div class="form_buttons" v-if="appraisalData.value.metaInfo.hasCurrentComponentAccess">
                <button type="button" class="btn btn-secondary text-white" @click="changeReadOnlyMode" v-if="!disableButton">{{ editButtonText }}</button>
                <button  class="btn btn-secondary text-white" :disabled="disableButton" v-if="!readOnlyMode">{{ buttonText }}</button>
            </div>
            <fieldset>
                <legend class="mb-4 text-uppercase">Probation Period Objectives</legend>
                <template v-for="(objective, key, index) in formData.set_objectives" :key="index">
                <label class="custom_label_style number_label" :for="['objective_'+objective.id]">{{index+1}}</label>
                    <div class="row">
                        <div class="col-lg-6">
                            <label class="custom_label_style" :for="['objective_'+objective.id]">Objective:</label>
                            <textarea class="form-control mb-3 disabled-textarea-objective" rows="3" placeholder="Describe the objective in details here .." :id="['objective_'+objective.id]" :disabled="readOnlyMode" 
                                v-model="formData.set_objectives['objective_'+index].name"></textarea>
                        </div>
                        <div class="col-lg-6">
                            <label class="custom_label_style" :for="['expected_outcome_'+objective.id]">Expected Outcome:</label>
                            <textarea class="form-control disabled-textarea-outcome" rows="3" placeholder="Expected outcome..." :id="['expected_outcome_'+objective.id]" :disabled="readOnlyMode" 
                                v-model="formData.set_objectives['objective_'+index].expected_outcome"></textarea>
                        </div>
                    </div>
                    <hr/>
                </template>
                <a href="#" class="btn-odoo" style="font-size: 14px;background: #875a7b;color: white;padding: 4px 12px;float: right;" @click.prevent="total_list_objectives_length++" v-if="!readOnlyMode">Add Line</a>
                </fieldset>
        </form>
    </div>
</div>
    `,
}
