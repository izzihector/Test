FieldFullForm = {
    inject: ['appraisalData'],
    data() {
        return {
            data: {}
        }
    },
    watch: {
        appraisalData: {
            handler(newVal, oldVal) {
                if (newVal.value) this.data = newVal.value
            },
            immediate: true,
            deep: true
        },
    },
    template: `
        <div>
            <a class="btn btn-secondary btn-sm btn-odoo" :href="'/report/pdf/nl_appraisal.report_employee_appraisal/' + data.id" v-if="data.metaInfo.state == 'done'">
                <i class="fa fa-view" /> 
                print
            </a>
            <div class="mt-4 custom_font_size">
                <h3>General Information</h3>
                <div class="row bg-white mt-2">
                    <div class="col-lg-2 border-grey border py-1 px-2 headr custom_font_size" >Employee Name:</div>
                    <div class="col-lg-4 border-grey border odoo-cell-grey py-1 px-2 custom_font_size">{{ data.employee_name }}</div>
                    <div class="col-lg-2 border-grey border py-1 px-2 headr custom_font_size">Office/ Duty station</div>
                    <div class="col-lg-4 border-grey border odoo-cell-grey py-1 px-2 custom_font_size">{{ data.office }}</div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-2 border-grey border py-1 px-2 headr custom_font_size">Position Title:</div>
                    <div class="col-lg-4 border-grey border odoo-cell-grey py-1 px-2 custom_font_size">{{ data.position }}</div>
                    <div class="col-lg-2 border-grey border py-1 px-2 headr custom_font_size" >Date of Evaluation:</div>
                    <div class="col-lg-4 border-grey border odoo-cell-grey py-1 px-2 custom_font_size">{{ data.create_date }}</div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-2 border-grey border py-1 px-2 headr custom_font_size">Review Period From:</div>
                    <div class="col-lg-4 border-grey border odoo-cell-grey py-1 px-2 custom_font_size">{{ data.from_date }}</div>
                    <div class="col-lg-2 border-grey border py-1 px-2 headr custom_font_size" >Review Period To:</div>
                    <div class="col-lg-4 border-grey border odoo-cell-grey py-1 px-2 custom_font_size">{{ data.to_date }}</div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-2 border-grey border py-1 px-2 headr custom_font_size">Supervisor:</div>
                    <div class="col-lg-4 border-grey border odoo-cell-grey py-1 px-2 custom_font_size">{{ data.manager_name }}</div>
                    <div class="col-lg-2 border-grey border py-1 px-2 headr custom_font_size" >Title:</div>
                    <div class="col-lg-4 border-grey border odoo-cell-grey py-1 px-2 custom_font_size">{{ data.manager_job }}</div>
                </div>
            </div>

            <div class="mt-5 custom_font_size">
                <div class="mb-3">
                    Average of the above ratings (can be weighted in the judgement of the evaluator based on performance throughout the review period.) 
                    <br/>
                    <strong> 
                        4.5 – 5 Exceptional/outstanding, 
                        3.5 – 4.4 Exceeds Expected Performance 2.5 – 3.4,          
                        Meets Expected Performance, 1.5 – 2.4          
                        Required performance improvement, 1 – 1.4             
                        Unsatisfactory/Unacceptable performance,
                     </strong>
                </div>
                <h4 >A.	Performance assessment by supervisor in discussion with employee:</h4>
                <div class="row bg-white mt-2">
                    <div class="col-lg-3 border-grey border py-1 px-2 headr" >Evaluation area</div>
                    <div class="col-lg-7 border-grey border py-1 px-2 headr" >Description/ Assessment question </div>
                    <div class="col-lg-2 border-grey border py-1 px-2 headr" >Ratings</div>
                    
                    <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">1. Work Performance</div>
                    <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">How is the employee performing his/her routine-tasks based on job description?</div>
                    <div class="col-lg-2 odoo-cell-grey d-flex align-items-center justify-content-center" style="padding: 0px"> {{ data.field_p1_rating1 }} </div>
                    
                    <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">2. Discipline</div>
                    <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">How disciplined or obedient is the employee?</div>
                    <div class="col-lg-2 odoo-cell-grey d-flex align-items-center justify-content-center" style="padding: 0px"> {{ data.field_p1_rating2 }} </div>
                    
                    <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">3. Behaviour</div>
                    <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">How is the overall behaviour and conduct of the employee, how does he/she behave with his/her other colleagues</div>
                    <div class="col-lg-2 odoo-cell-grey d-flex align-items-center justify-content-center" style="padding: 0px"> {{ data.field_p1_rating3 }} </div>
                    
                    <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">4. Punctuality</div>
                    <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">
                        How is the attendance and visibility of the employee during the official office hours?
                    </div>
                    <div class="col-lg-2 odoo-cell-grey d-flex align-items-center justify-content-center" style="padding: 0px"> {{ data.field_p1_rating4 }} </div>
                    
                    <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">5. Response to Instructions</div>
                    <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">
                        How does the employee take the formal instruction that you give to them as the supervisor? 
                        How quickly does the employee respond to the instructions, do they ignore instructions or delay in 
                        implementing the instructions?
                    </div>
                    <div class="col-lg-2 odoo-cell-grey d-flex align-items-center justify-content-center" style="padding: 0px"> {{ data.field_p1_rating5 }} </div>
                    
                    <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">6. Helpfulness & Initiative</div>
                    <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">
                        <strong>Does the employee</strong> show willingness to help others without being asked, suggests ideas, contributes to team building and volunteers when needed?
                    </div>
                    <div class="col-lg-2 odoo-cell-grey d-flex align-items-center justify-content-center" style="padding: 0px"> {{ data.field_p1_rating6 }} </div>
                    
                    <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">7. Respect SCA policies and Values</div>
                    <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">
                        Does your employee respect all the contents of SCA policies and values? Does the employee consider the policies and 
                        values before he/she decides to do something?
                        <br/>
                        <strong>SCA values: Responsiveness, Equality, Impartiality, Social Justice, and Integrity</strong>
                    </div>
                    <div class="col-lg-2 odoo-cell-grey d-flex align-items-center justify-content-center" style="padding: 0px"> {{ data.field_p1_rating7 }} </div>
                    
                    <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">8. Quality of Work</div>
                    <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">
                        Does the employee complete work/tasks to a high-level standard, pays attention to neatness and safety instructions?
                    </div>
                    <div class="col-lg-2 odoo-cell-grey d-flex align-items-center justify-content-center" style="padding: 0px"> {{ data.field_p1_rating8 }} </div>
                    
                    <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">9. Supervision</div>
                    <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">
                        Does the employee work independently with minimum supervision?  Does the employee remain calm and focused under pressure?
                    </div>
                    <div class="col-lg-2 odoo-cell-grey d-flex align-items-center justify-content-center" style="padding: 0px"> {{ data.field_p1_rating9 }} </div>
                    
                    <div class="col-lg-3 border-grey border py-1 px-2 odoo-cell-grey d-flex align-items-center">10. Efficiency</div>
                    <div class="col-lg-7 border-grey border py-1 px-2 odoo-cell-grey">
                        Does the employee appropriately use/utilize SCA assets, equipment and supplies given to him/her?
                    </div>
                    <div class="col-lg-2 odoo-cell-grey d-flex align-items-center justify-content-center" style="padding: 0px"> {{ data.field_p1_rating10 }} </div>
                    
                    <div class="col-lg-10 border-grey border py-1 px-2 odoo-cell-grey headr" >
                        Total score - Consolidated total 50/10. Sample rating. 40/10 = 4 (Above expected performance
                    </div>
                    <div class="col-lg-2 border-grey border d-flex align-items-center justify-content-center headr" style="padding: 0px"> {{ data.field_p1_total_score }} </div>
                </div>
            </div>

            <div class="mt-5 custom_font_size">
                <h4 >B.	Employee feedback (Capacity development and feedback about supervision)</h4>
                <div class="row bg-white">
                    <div class="col-lg-7 border-grey headr border-bottom-white border py-1 px-2">
                        Did the employee receive any trainings during the review period 
                        (both individual and group trainings apply)?
                    </div>
                    <div class="col-lg-5  border-grey border odoo-cell-grey py-1 px-2">
                        {{ data.field_p2_q1 }}
                        <br/>
                        <span v-if="data.field_p2_q1 == 'yes'">
                            <small class="text-muted"><strong>Type Of Training:</strong></small>
                            {{ data.field_p2_q1_training_type }}
                        </span>                           
                    </div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-7 border-grey headr border-bottom-white border py-1 px-2">
                        Is the level of supervision by your supervisor adequate and supportive?
                    </div>
                    <div class="col-lg-5  border-grey border odoo-cell-grey py-1 px-2">
                        {{ data.field_p2_q2 }}                         
                    </div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-7 border-grey headr border-bottom-white border py-1 px-2">
                        What training opportunities and support does the employee request for the next review period?
                    </div>
                    <div class="col-lg-5  border-grey border odoo-cell-grey py-1 px-2">
                        {{ data.field_p2_q3 }}                         
                    </div>
                </div>
                <div class="row bg-white">
                    <div class="col-lg-12 mt-3 question-text  px-2">
                        <h5>Employees Comments on his performance, Training and support accorded by supervisor during the review period:</h5>
                    </div>
                    <div class="col-lg-12 py-1 px-2 odoo-cell-grey">
                        {{ data.field_p2_emp_comments }}                         
                    </div>
                </div>
            </div>

            <div class="mt-5 custom_font_size">
                <h4>C. Line Supervisor and overall performance rating and way forward</h4>
                <div class="row bg-white">
                    <div class="col-lg-3 border-grey headr  border py-1 px-2" >
                        <strong>Rate</strong>
                    </div>
                    <div class="col-lg-6 border-grey headr  border py-1 px-2" >
                        <strong>Interpretaion</strong>
                    </div>
                    <div class="col-lg-3 border-grey headr  border py-1 px-2" >
                        <strong>Supervisor final rating</strong>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-9 p-0">
                        <div class="row bg-white">
                            <div class="col-lg-4 border-grey odoo-cell-grey  border py-1 px-2">4.5 – 5</div>
                            <div class="col-lg-8 border-grey odoo-cell-grey  border py-1 px-2">Exceptional/Outstanding</div>
                        </div>
                        <div class="row bg-white">
                            <div class="col-lg-4 border-grey odoo-cell-grey  border py-1 px-2">3.5 – 4.4</div>
                            <div class="col-lg-8 border-grey odoo-cell-grey  border py-1 px-2">Exceeds Expected Performance</div>
                        </div>
                        <div class="row bg-white">
                            <div class="col-lg-4 border-grey odoo-cell-grey  border py-1 px-2">2.5 – 3.4</div>
                            <div class="col-lg-8 border-grey odoo-cell-grey  border py-1 px-2">Meets Expected Performance</div>
                        </div>
                        <div class="row bg-white">
                            <div class="col-lg-4 border-grey odoo-cell-grey  border py-1 px-2">1.5 – 2.4 </div>
                            <div class="col-lg-8 border-grey odoo-cell-grey  border py-1 px-2">Required performance improvement</div>
                        </div>
                        <div class="row bg-white">
                            <div class="col-lg-4 border-grey odoo-cell-grey  border py-1 px-2">1 – 1.4 </div>
                            <div class="col-lg-8 border-grey odoo-cell-grey  border py-1 px-2">Unsatisfactory/Unacceptable Performance</div>
                        </div>
                        <div class="row bg-white">
                            <div class="col-lg-4 border-grey odoo-cell-grey  border py-1 px-2">Not Applicable</div>
                            <div class="col-lg-8 border-grey odoo-cell-grey  border py-1 px-2">Not Applicable or Not Able to Evaluate</div>
                        </div>
                    </div>
                    <div class="col-lg-3 odoo-cell-grey">
                        <div class="d-flex justify-content-center align-items-center" style="height:100%; flex-direction:column; text-align:center;">
                            <span v-if="data.p7_overall_rating_not_applicable">Not Applicable</span>
                            <template v-else="">
                                <span>{{data.p7_overall_rating}}</span>
                                <span class="mt-2" style="font-size:12px;">{{ data.p7_overall_rating >= 4.5 ? 'Exceptional/Outstanding' : data.p7_overall_rating >= 3.5 ? 'Exceeds Expected Performance' : data.p7_overall_rating >= 2.5 ? 'Meets Expected Performance' : data.p7_overall_rating >= 1.5 ? 'Required Performance Improvement' : data.p7_overall_rating >= 1 ? 'Unsatisfactory/Unacceptable Performance' : ''  }}</span>
                            </template>
                        </div>
                    </div>
                </div>
            </div>

            <div class="mt-5 custom_font_size">
                <h4 >D.	Overall rating</h4>
                <div class="row bg-white">
                    <div class="col-lg-12 mt-3 question-text  px-2">
                        <h5>Supervisor/Evaluator’s Comments and recommendation:</h5>
                    </div>
                    <div class="col-lg-12 py-1 odoo-cell-grey px-2">
                        {{ data.field_overall_assessment }}                         
                    </div>
                </div>

            </div>
            
            <div class="mt-5" v-if="data.manager_sign_date">
                <h4>Signed by:</h4>
                <div>
                    <strong>Supervisor:</strong> {{ data.manager_name }} on {{ data.manager_sign_date }}
                </div>
            </div>
        </div>
    `
}